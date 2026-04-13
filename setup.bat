@echo off
REM Quick setup script for My Agent on Windows

echo.
echo ╭─────────────────────────────────────────╮
echo │    🤖 My Agent Quick Setup v0.1.0      │
echo ╰─────────────────────────────────────────╯
echo.

REM Check Python version
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.11+ first.
    exit /b 1
)

python --version
echo ✓ Python detected

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
) else (
    echo ✓ Virtual environment already exists
)

REM Activate venv
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
python -m pip install --upgrade pip setuptools wheel > nul 2>&1
pip install -e . > nul 2>&1

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Copy .env.example to .env:
echo    copy .env.example .env
echo.
echo 2. Edit .env and add your API key:
echo    - For Anthropic: ANTHROPIC_API_KEY=sk-ant-...
echo    - For OpenAI: OPENAI_API_KEY=sk-...
echo    - For OpenRouter: OPENROUTER_API_KEY=sk-or-...
echo.
echo 3. Run the agent:
echo    python main.py
echo.
echo 4. Or try a single query:
echo    python main.py "What is 2 + 2?"
echo.
