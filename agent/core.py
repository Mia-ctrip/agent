#!/usr/bin/env python3
"""
Core Agent Module

A minimal AI agent that can execute tool-calling loops.
Supports OpenAI, Anthropic, and OpenRouter.
"""

import json
import logging
import os
import inspect
from typing import Any, Dict, List, Optional, get_type_hints
from dataclasses import dataclass, asdict
from pathlib import Path

import anthropic
from openai import OpenAI as OpenAIClient
from tools.tool_register import ToolRegistry

from prompt.prompt_builder import (
    DEFAULT_AGENT_IDENTITY,
    MEMORY_GUIDANCE
)

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a conversation message."""
    role: str  # "user", "assistant"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None  # For assistant messages with tool calls
    tool_call_id: Optional[str] = None  # For user messages with tool results


class Agent:
    """
    Minimal AI Agent with tool-calling support.

    Features:
    - Multi-turn conversation
    - Tool calling loop
    - Multiple provider support
    - Simple message history
    """

    def __init__(
        self,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_turns: int = 10,
        system_prompt: Optional[str] = None,
        history_file: Optional[str] = None,
        tools: Optional[List] = None,
        tool_registry: Optional[ToolRegistry] = None,
        enable_auto_memory: bool = True,
    ):
        """
        Initialize the Agent.

        Args:
            model: LLM model name (defaults to env var LLM_MODEL)
            provider: Provider name: "openai", "anthropic", "openrouter"
            api_key: API key (defaults to env var)
            base_url: Custom API base URL
            max_turns: Maximum tool-calling iterations
            system_prompt: System prompt for the agent
            history_file: Path to conversation history file (defaults to history_conversation.json)
            enable_auto_memory: Enable automatic learning from user corrections
        """
        self.model = model or os.getenv("LLM_MODEL", "MiniMax-M2.7")
        self.provider = (provider or os.getenv("LLM_PROVIDER", "anthropic")).lower()
        self.api_key = api_key or os.getenv("api_key", " ")
        self.base_url = base_url or os.getenv("base_url")
        self.max_turns = max_turns
        self.enable_auto_memory = enable_auto_memory

        # Setup paths
        self.memory_dir = Path("./memory")
        self.memory_dir.mkdir(exist_ok=True)
        self.memory_index = self.memory_dir / "MEMORY.md"
        self.history_file = Path(history_file) if history_file else self.memory_dir / "history_conversation.json"

        self.load_system_prompt()
        # Load conversation history from disk
        self.conversation_history: List[Message] = []
        self._load_history()

        self._load_tools(tools or [])
        # Initialize API client based on provider
        self._init_client()

    def _resolve_api_key(self) -> str:
        """Resolve API key from environment based on provider."""
        if self.provider == "openai":
            return os.getenv("OPENAI_API_KEY", "")
        elif self.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY", "")
        elif self.provider == "openrouter":
            return os.getenv("OPENROUTER_API_KEY", "")
        return ""

    def _init_client(self) -> None:
        """Initialize the appropriate API client."""
        if not self.api_key:
            raise ValueError(
                f"No API key found for provider '{self.provider}'. "
                f"Set the appropriate environment variable."
            )

        if self.provider == "anthropic":
            self.client = anthropic.Anthropic()
        elif self.provider in ("openai", "openrouter"):
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self.client = OpenAIClient(**kwargs)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def run_conversation(self, user_message: str) -> str:
        """
        Run a single turn of conversation with tool calling.

        Args:
            user_message: The user's input message

        Returns:
            The final response from the agent
        """
        # Check if user is correcting a previous mistake
        if self.enable_auto_memory and len(self.conversation_history) > 0:
            self._detect_and_save_correction(user_message)

        # Add user message to history
        self.conversation_history.append(Message("user", user_message))
        self._save_history()

        logger.debug(f"User: {user_message}")

        # Tool calling loop
        for turn in range(self.max_turns):
            # Call the LLM
            response = self._call_llm()

            # Save assistant response with tool calls if any
            if response["role"] == "assistant":
                self.conversation_history.append(
                    Message(
                        role="assistant",
                        content=response["content"],
                        tool_calls=response.get("tool_calls")
                    )
                )
                self._save_history()

            # Check if we're done (no tool calls)
            if response["role"] == "assistant" and not response.get("tool_calls"):
                logger.info(f"Agent: {response['content']}")
                return response["content"]

            # Process tool calls if any
            if response.get("tool_calls"):
                for tool_call in response["tool_calls"]:
                    tool_name = tool_call["name"]
                    tool_input = tool_call["arguments"]
                    tool_id = tool_call.get("id", "")

                    if tool_name not in self.tool_registry.tools:
                        logger.warning(f"Unknown tool: {tool_name}")
                        continue

                    logger.info(f"Calling tool: {tool_name} with {tool_input}")

                    # Execute the tool
                    try:
                        result = self.tool_registry.call_function(tool_name, **tool_input)
                        logger.info(f"Tool result: {result}")
                    except Exception as e:
                        result = f"Error: {str(e)}"
                        logger.error(f"Tool execution failed: {e}")

                    # Add tool result to history
                    self.conversation_history.append(
                        Message(
                            role="user",
                            content=f"[Tool result for {tool_name}]: {result}",
                            tool_call_id=tool_id
                        )
                    )
                    self._save_history()

        logger.warning("Max turns reached without completion")
        return "Max turns reached. Agent could not complete the task."

    def _call_llm(self) -> Dict[str, Any]:
        """
        Call the LLM with current conversation history.

        Returns:
            Response dict with role, content, and optional tool_calls
        """
        messages = []
        for msg in self.conversation_history:
            message_dict = {"role": msg.role, "content": msg.content}

            # Add tool_calls if present (for OpenAI-compatible APIs)
            if msg.tool_calls and self.provider != "anthropic":
                message_dict["tool_calls"] = msg.tool_calls

            # Add tool_call_id if present (for tool results)
            if msg.tool_call_id and self.provider != "anthropic":
                message_dict["tool_call_id"] = msg.tool_call_id

            messages.append(message_dict)

        if self.provider == "anthropic":
            return self._call_anthropic(messages)
        else:
            return self._call_openai_compatible(messages)

    def _call_anthropic(self, messages: List[Dict]) -> Dict[str, Any]:
        """Call Anthropic API with tool support."""

        # Convert messages to Anthropic format with content blocks
        anthropic_messages = []
        for msg in self.conversation_history:
            content_blocks = []

            # Add text content if present
            if msg.content:
                content_blocks.append({"type": "text", "text": msg.content})

            # Add tool_use blocks for assistant messages
            if msg.role == "assistant" and msg.tool_calls:
                for tc in msg.tool_calls:
                    content_blocks.append({
                        "type": "tool_use",
                        "id": tc["id"],
                        "name": tc["name"],
                        "input": tc["arguments"]
                    })

            # Add tool_result blocks for user messages with tool results
            if msg.role == "user" and msg.tool_call_id:
                # Replace text content with tool_result block
                content_blocks = [{
                    "type": "tool_result",
                    "tool_use_id": msg.tool_call_id,
                    "content": msg.content
                }]

            # Use content blocks if we have them, otherwise use plain text
            anthropic_messages.append({
                "role": msg.role,
                "content": content_blocks if content_blocks else msg.content
            })

        # Call API
        kwargs = {
            "model": self.model,
            "system": self.system_prompt,
            "max_tokens": 5120,
            "messages": anthropic_messages,
        }

        # Add tools if available
        if self.tool_registry and self.tool_registry.tools:
            kwargs["tools"] = self.tool_registry.get_anthropic_function_definitions()

        response = self.client.messages.create(**kwargs)

        # Extract content and tool calls
        content = ""
        tool_calls = []

        for block in response.content:
            if hasattr(block, "text"):
                content = block.text
            elif hasattr(block, "type") and block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "arguments": block.input,
                })

        return {
            "role": "assistant",
            "content": content,
            "tool_calls": tool_calls,
        }


    
    def _call_openai_compatible(self, messages: List[Dict]) -> Dict[str, Any]:
        """Call OpenAI-compatible API."""
        # Add tools if available
        tools = None
        if self.tool_registry and self.tool_registry.tools:
            tools = self.tool_registry.get_openai_function_definitions()

        kwargs = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1024,
        }
        if tools:
            kwargs["tools"] = tools

        response = self.client.chat.completions.create(**kwargs)

        # Parse tool calls from response
        tool_calls = []
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            for tc in response.choices[0].message.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                })

        return {
            "role": "assistant",
            "content": response.choices[0].message.content or "",
            "tool_calls": tool_calls,
        }

    def reset_history(self) -> None:
        """Clear conversation history and remove history file."""
        self.conversation_history.clear()
        # Remove history file if it exists
        if self.history_file.exists():
            self.history_file.unlink()
        logger.info("Conversation history cleared")

    def load_system_prompt(self) -> str:
        '''
        Load system_prompt including learned memories.
        1. Default agent identity
        2. Memory guidance
        3. Learned feedback from past mistakes
        '''
        default_prompt = DEFAULT_AGENT_IDENTITY
        memory_prompt = MEMORY_GUIDANCE

        # Load learned feedback (check if method exists, as this might be called during __init__)
        learned_feedback = ""
        if self.enable_auto_memory and hasattr(self, 'memory_dir'):
            learned_feedback = self._load_memory_content()

        self.system_prompt = default_prompt + "\n\n" + memory_prompt
        if learned_feedback:
            self.system_prompt += "\n\n" + learned_feedback

    def _load_tools(self, tools: List) -> None:
        """Load tools into the agent."""
        self.tool_registry = ToolRegistry()

        # Register tools from the tools list
        for tool in tools:
            self.tool_registry.register(
                type=tool.get("type", "function"),
                name=tool["name"],
                description=tool["description"],
                params=tool["parameters"],
                func=tool["func"]
            )

        logger.info(f"Loaded {len(tools)} tools into the agent")        

    def get_history(self) -> List[Dict[str, Any]]:
        """Get conversation history as dict list."""
        return [asdict(msg) for msg in self.conversation_history]

    def _save_history(self) -> None:
        """Save conversation history to disk."""
        try:
            history_data = [asdict(msg) for msg in self.conversation_history]
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved conversation history to {self.history_file}")
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def _load_history(self) -> None:
        """Load conversation history from disk."""
        if not self.history_file.exists():
            logger.info("No history file found, starting fresh")
            return

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                history_data = json.load(f)

            self.conversation_history = [
                Message(
                    role=msg["role"],
                    content=msg["content"],
                    tool_calls=msg.get("tool_calls"),
                    tool_call_id=msg.get("tool_call_id")
                )
                for msg in history_data
            ]
            logger.info(f"Loaded {len(self.conversation_history)} messages from {self.history_file}")
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            self.conversation_history = []

    def _detect_and_save_correction(self, user_message: str) -> None:
        """Detect if user is correcting a mistake and save to memory."""
        # Keywords that indicate correction
        correction_indicators = [
            "不对", "错了", "不是", "应该", "先", "记住", "以后",
            "别", "不要", "必须", "一定要", "不能", "before", "first",
            "wrong", "no", "should", "must", "don't", "never", "always"
        ]

        # Check if message contains correction indicators
        message_lower = user_message.lower()
        is_correction = any(indicator in message_lower for indicator in correction_indicators)

        if not is_correction:
            return

        # Get recent conversation context (last 10 messages)
        recent_history = self.conversation_history[-10:] if len(self.conversation_history) > 10 else self.conversation_history

        # Use LLM to analyze and generate memory
        try:
            logger.info("Detected potential correction, generating memory...")
            memory_content = self._generate_feedback_memory(recent_history, user_message)

            if memory_content:
                self._save_feedback_memory(memory_content)
                logger.info("✅ Saved feedback to memory")
        except Exception as e:
            logger.error(f"Failed to save correction to memory: {e}")

    def _generate_feedback_memory(self, recent_history: List[Message], correction: str) -> Optional[str]:
        """Use LLM to generate structured feedback memory."""

        # Build context from recent history
        context = []
        for msg in recent_history:
            role_label = "User" if msg.role == "user" else "Agent"
            context.append(f"{role_label}: {msg.content}")
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    context.append(f"  → Tool called: {tc['name']}({tc['arguments']})")

        context_str = "\n".join(context)

        prompt = f"""Based on the conversation history and the user's correction, generate a feedback memory entry.

Conversation history:
{context_str}

User's correction: {correction}

Analyze what went wrong and generate a structured feedback in this format:

**Rule:** [What the agent should do differently - one clear sentence]

**Why:** [Why the previous approach was wrong - explain the root cause]

**How to apply:** [Specific instructions on when and how to apply this rule]

**What went wrong:** [Brief description of the mistake that was made]

Keep it concise and actionable. Focus on the specific mistake and how to avoid it in the future.
"""

        try:
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1024
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Failed to generate memory: {e}")
            return None

    def _save_feedback_memory(self, memory_content: str) -> None:
        """Save feedback memory to disk."""
        import time
        import re

        # Generate filename from timestamp
        timestamp = int(time.time())
        filename = f"feedback_{timestamp}.md"
        filepath = self.memory_dir / filename

        # Extract title from content (first line or first sentence)
        first_line = memory_content.split('\n')[0].strip()
        # Remove markdown formatting
        title = re.sub(r'\*\*|\[|\]|\(|\)', '', first_line)[:60]

        # Create memory file with frontmatter
        frontmatter = f"""---
name: {title}
description: Auto-generated from user correction
type: feedback
---

{memory_content}
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(frontmatter)

        # Update MEMORY.md index
        self._update_memory_index(filename, title)

    def _update_memory_index(self, filename: str, title: str) -> None:
        """Update MEMORY.md with new memory entry."""
        index_entry = f"- [{title}]({filename}) — Auto-learned from user correction\n"

        if self.memory_index.exists():
            content = self.memory_index.read_text(encoding="utf-8")
            if filename not in content:
                content += index_entry
                self.memory_index.write_text(content, encoding="utf-8")
        else:
            header = "# Agent Memory\n\nLessons learned from user corrections:\n\n"
            self.memory_index.write_text(header + index_entry, encoding="utf-8")

    def _load_memory_content(self) -> str:
        """Load all memory content to include in system prompt."""
        if not self.memory_index.exists():
            return ""

        memory_files = list(self.memory_dir.glob("feedback_*.md"))
        if not memory_files:
            return ""

        memories = []
        for mem_file in memory_files[:10]:  # Limit to 10 most recent
            try:
                content = mem_file.read_text(encoding="utf-8")
                # Remove frontmatter
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        content = parts[2].strip()
                memories.append(content)
            except Exception as e:
                logger.warning(f"Failed to load memory {mem_file}: {e}")

        if memories:
            return "\n\n=== LEARNED FROM PAST MISTAKES ===\n" + "\n\n---\n\n".join(memories)
        return ""

