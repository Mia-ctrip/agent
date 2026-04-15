#!/usr/bin/env python3
"""
Test script to verify tool registration.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.core import Agent
from tools.tools_config import TOOLS

def test_tool_registration():
    """Test that tools are properly registered."""
    print("Testing tool registration...")

    # Create agent with tools
    try:
        agent = Agent(tools=TOOLS)

        print(f"\n✅ Agent created successfully")
        print(f"Provider: {agent.provider}")
        print(f"Model: {agent.model}")
        print(f"\n📦 Registered tools ({len(agent.tool_registry.tools)}):")

        for tool_name, tool_info in agent.tool_registry.tools.items():
            print(f"  - {tool_name}: {tool_info['description'][:60]}...")

        print("\n✅ All tools registered successfully!")

        # Test Anthropic function definitions
        print("\n🔧 Testing Anthropic function definitions:")
        anthropic_defs = agent.tool_registry.get_anthropic_function_definitions()
        print(f"  Generated {len(anthropic_defs)} Anthropic tool definitions")

        # Test OpenAI function definitions
        print("\n🔧 Testing OpenAI function definitions:")
        openai_defs = agent.tool_registry.get_openai_function_definitions()
        print(f"  Generated {len(openai_defs)} OpenAI tool definitions")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tool_registration()
    sys.exit(0 if success else 1)