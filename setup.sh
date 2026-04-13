#!/bin/bash
# Quick setup script for My Agent

set -e

echo "╭─────────────────────────────────────────╮"
echo "│    🤖 My Agent Quick Setup v0.1.0      │"
echo "╰─────────────────────────────────────────╯"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION detected"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate venv
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip setuptools wheel > /dev/null
pip install -e "." > /dev/null

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env:"
echo "   cp .env.example .env"
echo ""
echo "2. Edit .env and add your API key:"
echo "   - For Anthropic: ANTHROPIC_API_KEY=sk-ant-..."
echo "   - For OpenAI: OPENAI_API_KEY=sk-..."
echo "   - For OpenRouter: OPENROUTER_API_KEY=sk-or-..."
echo ""
echo "3. Run the agent:"
echo "   python main.py"
echo ""
echo "4. Or try a single query:"
echo "   python main.py \"What is 2 + 2?\""
echo ""
