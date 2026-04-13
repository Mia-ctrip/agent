"""Built-in tools for the agent."""

import json
import logging

logger = logging.getLogger(__name__)


def calculator(operation: str, a: float, b: float) -> float:
    """
    Simple calculator tool.

    Args:
        operation: "+", "-", "*", "/"
        a: First number
        b: Second number

    Returns:
        The calculation result
    """
    ops = {
        "+": lambda x, y: x + y,
        "-": lambda x, y: x - y,
        "*": lambda x, y: x * y,
        "/": lambda x, y: x / y if y != 0 else None,
    }

    if operation not in ops:
        raise ValueError(f"Unknown operation: {operation}")

    result = ops[operation](a, b)
    if result is None:
        raise ValueError("Division by zero")

    return result


def web_search(query: str) -> str:
    """
    Placeholder web search tool.

    In a real implementation, this would call an API like Exa, Google, or Bing.

    Args:
        query: Search query string

    Returns:
        Search results as JSON string
    """
    # This is a placeholder - in a real app, integrate with Exa, Google, etc.
    mock_results = {
        "query": query,
        "results": [
            {
                "title": "Example Result 1",
                "url": "https://example.com/1",
                "snippet": "This is a mock search result."
            }
        ],
        "note": "This is a mock tool. Integrate with real search API."
    }
    return json.dumps(mock_results)


def get_example_tool() -> dict:
    """Return an example tool definition."""
    return {
        "name": "calculator",
        "description": "Performs basic arithmetic operations",
        "func": calculator,
    }
