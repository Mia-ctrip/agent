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
        """
        self.model = model or os.getenv("LLM_MODEL", "MiniMax-M2.7")
        self.provider = (provider or os.getenv("LLM_PROVIDER", "anthropic")).lower()
        self.api_key = api_key or os.getenv("api_key", " ")
        self.base_url = base_url or os.getenv("base_url")
        self.max_turns = max_turns

        # Setup history file path
        self.history_file = Path(history_file) if history_file else Path("history_conversation.json")

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
        # Add user message to history
        self.conversation_history.append(Message("user", user_message))
        self._save_history()

        logger.debug(f"User: {user_message}")

        # Tool calling loop
        for turn in range(self.max_turns):
            # Call the LLM
            response = self._call_llm()

            if response["role"] == "assistant":
                self.conversation_history.append(
                    Message("assistant", response["content"])
                )
                self._save_history()

            # Check if we're done (no tool calls)
            if response["role"] == "assistant" and not response.get("tool_calls"):
                logger.debug(f"Agent: {response['content']}")
                return response["content"]

            # Process tool calls if any
            if response.get("tool_calls"):
                for tool_call in response["tool_calls"]:
                    tool_name = tool_call["name"]
                    tool_input = tool_call["arguments"]

                    if tool_name not in self.tool_registry.tools:
                        logger.warning(f"Unknown tool: {tool_name}")
                        continue

                    logger.debug(f"Calling tool: {tool_name} with {tool_input}")

                    # Execute the tool
                    try:
                        result = self.tool_registry.call_function(tool_name, **tool_input)
                        logger.debug(f"Tool result: {result}")
                    except Exception as e:
                        result = f"Error: {str(e)}"
                        logger.error(f"Tool execution failed: {e}")

                    # Add tool result to history
                    self.conversation_history.append(
                        Message("user", f"[Tool result: {result}]")
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
        messages = [{"role": msg.role, "content": msg.content}
                    for msg in self.conversation_history]

        if self.provider == "anthropic":
            return self._call_anthropic(messages)
        else:
            return self._call_openai_compatible(messages)

    def _call_anthropic(self, messages: List[Dict]) -> Dict[str, Any]:
        """Call Anthropic API with tool support."""

        # Call API
        kwargs = {
            "model": self.model,
            "system": self.system_prompt,
            "max_tokens": 5120,
            "messages": messages,
        }

        # Add tools if available
        if self.tool_registry:
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
        load system_prompt
        1. persistent system prompt
        '''
        default_prompt = DEFAULT_AGENT_IDENTITY
        memory_prompt = MEMORY_GUIDANCE
        self.system_prompt =  default_prompt + ";" +(memory_prompt)

    def _load_tools(self, tools: List) -> None:
        """Load tools into the agent."""
        self.tool_registry = ToolRegistry()
        
        logger.info(f"Loaded {len(tools)} tools into the agent")        

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history as dict list."""
        return [{"role": msg.role, "content": msg.content}
                for msg in self.conversation_history]

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
                Message(role=msg["role"], content=msg["content"])
                for msg in history_data
            ]
            logger.info(f"Loaded {len(self.conversation_history)} messages from {self.history_file}")
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            self.conversation_history = []
