#!/bin/bash

# AIOSv3 Startup Script

set -e

echo "🚀 Starting AIOSv3 - AI Agent Platform"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check for Python 3.12
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD=python3.12
    python_version=$(python3.12 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "✅ Found Python $python_version"
else
    echo "❌ Error: Python 3.12 not found"
    echo "   Please install Python 3.12 using:"
    echo "   brew install python@3.12"
    echo "   or visit https://python.org/downloads"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip first
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -e .

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before proceeding"
    echo "   Required: ANTHROPIC_API_KEY or OPENAI_API_KEY"
fi

# Run setup test
echo "🧪 Running setup test..."
$PYTHON_CMD scripts/test_setup.py

echo ""
echo "✅ AIOSv3 is ready!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys (if not done already)"
echo "2. Start the API server:"
echo "   python -m api.main"
echo ""
echo "3. Or run in development mode:"
echo "   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "4. Visit the API docs at:"
echo "   http://localhost:8000/docs"
echo ""
echo "5. Chat with your CTO Agent:"
echo "   curl -X POST http://localhost:8000/cto/chat \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"message\": \"Hello, I need help planning a new project\"}'"