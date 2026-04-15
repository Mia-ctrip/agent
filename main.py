#!/usr/bin/env python3
"""
Main CLI Entry Point

Start the agent with an interactive conversation loop.

Usage:
    python main.py                              # Interactive mode
    python main.py "Your question here"         # Single query
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional


from rich.console import Console
from rich.markdown import Markdown

from tools.tool_register import ToolRegistry

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.core import Agent
from tools.builtin_tools import calculator, web_search

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Rich console for pretty output
console = Console()


def print_banner():
    """Print welcome banner."""
    banner = """
    ╭─────────────────────────────────────────╮
    │        🤖 My GPU Agent v0.1.0           │
    │    A minimal AI agent framework         │
    ╰─────────────────────────────────────────╯
    """
    console.print(banner, style="cyan")


def interactive_mode(agent: Agent) -> None:
    """Run interactive conversation mode."""
    console.print("[bold cyan]Interactive Mode[/bold cyan]")
    console.print("Type 'quit' or 'exit' to leave\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit"):
                console.print("[bold]Goodbye![/bold]")
                break

            if user_input.lower() == "/reset":
                agent.reset_history()
                console.print("[yellow]Conversation history cleared[/yellow]")
                continue

            if user_input.lower() == "/history":
                history = agent.get_history()
                console.print("\n[bold]Conversation History:[/bold]")
                for msg in history:
                    role = "[bold cyan]User[/bold cyan]" if msg["role"] == "user" else "[bold green]Agent[/bold green]"
                    console.print(f"{role}: {msg['content']}")
                console.print()
                continue

            # Run the agent
            console.print("\n[bold green]Agent:[/bold green]", end=" ")
            response = agent.run_conversation(user_input)
            console.print(response)
            console.print()

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Interrupted[/bold yellow]")
            break
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            console.print(f"[bold red]Error: {e}[/bold red]")


def single_query_mode(agent: Agent, query: str) -> None:
    """Run a single query and exit."""
    try:
        console.print(f"[bold cyan]Query:[/bold cyan] {query}\n")
        response = agent.run_conversation(query)
        console.print(f"[bold green]Response:[/bold green]\n{response}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        console.print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)


def setup_agent() -> Agent:
    """Create and configure the agent."""
    # Load environment variables from .env
    from dotenv import load_dotenv
    load_dotenv()

    # Create agent
    agent = Agent()

    # Register built-in tools
    agent.register_tool(
        "calculator",
        calculator,
        "Performs basic arithmetic operations (add, subtract, multiply, divide)"
    )
    agent.register_tool(
        "web_search",
        web_search,
        "Search the web for information (placeholder - returns mock results)"
    )

    return agent


def main():
    """Main entry point."""
    print_banner()

    # Setup agent
    agent = setup_agent()
    console.print(f"[bold]Model:[/bold] {agent.model}")
    console.print(f"[bold]Provider:[/bold] {agent.provider}\n")

    # Determine mode
    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        single_query_mode(agent, query)
    else:
        # Interactive mode
        interactive_mode(agent)


if __name__ == "__main__":
    main()
