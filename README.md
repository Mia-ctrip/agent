# My Agent 🤖

A minimal AI agent project based on the Hermes Agent architecture.

## Quick Start

### 1. Install Dependencies

```bash
cd d:/agent/my-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e "."
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your API key:

```bash
cp .env.example .env
```

Choose your LLM provider:

**Option A: Anthropic (Claude)**
```bash
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-opus-4-20250514
LLM_PROVIDER=anthropic
```

**Option B: OpenAI (GPT-4)**
```bash
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o
LLM_PROVIDER=openai
```

**Option C: OpenRouter (200+ models)**
```bash
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=anthropic/claude-opus-4:beta
LLM_PROVIDER=openrouter
```

### 3. Run the Agent

Interactive mode:
```bash
python main.py
```

Single query:
```bash
python main.py "What is 2 + 2?"
```

## Project Structure

```
my-agent/
├── agent/
│   ├── __init__.py
│   └── core.py              # Agent implementation
├── tools/
│   ├── __init__.py
│   └── builtin_tools.py     # Calculator, web search, etc.
├── main.py                  # CLI entry point
├── pyproject.toml           # Project config
├── .env.example             # Configuration template
└── README.md               # This file
```

## Features

- ✅ Multi-turn conversations
- ✅ Tool registration system
- ✅ Multiple provider support (Anthropic, OpenAI, OpenRouter)
- ✅ Simple message history
- ✅ Interactive CLI
- ✅ Built-in tools (calculator, web search placeholder)

## Interactive Commands

- `quit` / `exit` - Leave the agent
- `/reset` - Clear conversation history
- `/history` - Show conversation history

## Next Steps

### Add More Tools

Edit `tools/builtin_tools.py`:

```python
def my_tool(param1: str, param2: int) -> str:
    """Tool description."""
    return f"Result: {param1} x {param2}"

# In setup_agent() in main.py:
agent.register_tool(
    "my_tool",
    my_tool,
    "Description of what this tool does"
)
```

### Customize the Agent

Edit `agent/core.py` to add:
- Tool calling support (currently basic)
- Memory/knowledge base integration
- Streaming responses
- Custom response formatting

### Add a Web Interface

Create `web.py` with FastAPI:
```python
from fastapi import FastAPI
from agent.core import Agent

app = FastAPI()
agent = Agent()

@app.post("/chat")
async def chat(message: str):
    return {"response": agent.run_conversation(message)}
```

## Troubleshooting

**"No API key found" error:**
- Make sure `.env` file is created and has your API key
- Check the correct environment variable name for your provider

**"Module not found" error:**
- Make sure to run `pip install -e "."` in the project directory
- Activate the virtual environment

**Rate limit errors:**
- Check your API provider's rate limits
- Add retry logic in `agent/core.py`

## Configuration

All settings are loaded from `.env`:
- `LLM_MODEL` - Model name
- `LLM_PROVIDER` - Provider name
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING)
- `MAX_TURNS` - Maximum agent iterations

## License

MIT
