#!/usr/bin/env python3
"""
Core Agent Module

A minimal AI agent that can execute tool-calling loops.
Supports OpenAI, Anthropic, and OpenRouter.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from anthropic import Anthropic as AnthropicClient
from openai import OpenAI as OpenAIClient

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
        """
        self.model = model or os.getenv("LLM_MODEL", "MiniMax-M2.7")
        self.provider = (provider or os.getenv("LLM_PROVIDER", "anthropic")).lower()
        self.api_key = api_key or self._resolve_api_key()
        self.base_url = base_url or os.getenv("OPENROUTER_BASE_URL")
        self.max_turns = max_turns

        self.system_prompt = (
            system_prompt
            or "You are a helpful AI assistant. Be concise and helpful."
        )

        self.conversation_history: List[Message] = []
        self.tools: Dict[str, Any] = {}
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
            self.client = AnthropicClient(api_key=self.api_key)
        elif self.provider in ("openai", "openrouter"):
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self.client = OpenAIClient(**kwargs)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def register_tool(self, name: str, func, description: str) -> None:
        """
        Register a tool the agent can call.

        Args:
            name: Tool name (used in function calling)
            func: Callable that implements the tool
            description: Human-readable description
        """
        self.tools[name] = {
            "name": name,
            "func": func,
            "description": description,
        }
        logger.info(f"Registered tool: {name}")

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

        logger.debug(f"User: {user_message}")

        # Tool calling loop
        for turn in range(self.max_turns):
            # Call the LLM
            response = self._call_llm()

            if response["role"] == "assistant":
                self.conversation_history.append(
                    Message("assistant", response["content"])
                )

            # Check if we're done (no tool calls)
            if response["role"] == "assistant" and not response.get("tool_calls"):
                logger.debug(f"Agent: {response['content']}")
                return response["content"]

            # Process tool calls if any
            if response.get("tool_calls"):
                for tool_call in response["tool_calls"]:
                    tool_name = tool_call["name"]
                    tool_input = tool_call["arguments"]

                    if tool_name not in self.tools:
                        logger.warning(f"Unknown tool: {tool_name}")
                        continue

                    logger.debug(f"Calling tool: {tool_name} with {tool_input}")

                    # Execute the tool
                    try:
                        result = self.tools[tool_name]["func"](**tool_input)
                        logger.debug(f"Tool result: {result}")
                    except Exception as e:
                        result = f"Error: {str(e)}"
                        logger.error(f"Tool execution failed: {e}")

                    # Add tool result to history
                    self.conversation_history.append(
                        Message("user", f"[Tool result: {result}]")
                    )

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
        """Call Anthropic API."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self.system_prompt,
            messages=messages,
        )

        return {
            "role": "assistant",
            "content": response.content[0].text,
            "tool_calls": [],
        }

    def _call_openai_compatible(self, messages: List[Dict]) -> Dict[str, Any]:
        """Call OpenAI-compatible API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1024,
        )

        return {
            "role": "assistant",
            "content": response.choices[0].message.content or "",
            "tool_calls": [],
        }

    def reset_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history as dict list."""
        return [{"role": msg.role, "content": msg.content}
                for msg in self.conversation_history]
