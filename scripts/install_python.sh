#!/bin/bash

# Python 3.12 Installation Script for macOS

echo "🐍 Python 3.12 Installation Helper"
echo "=================================="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Installing Homebrew first..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew is installed"
fi

echo ""
echo "📦 Installing Python 3.12..."
brew install python@3.12

echo ""
echo "🔗 Creating python3.12 symlink..."
brew link python@3.12

# Check if installation was successful
if command -v python3.12 &> /dev/null; then
    echo ""
    echo "✅ Python 3.12 installed successfully!"
    python3.12 --version
    
    echo ""
    echo "📍 Python 3.12 location:"
    which python3.12
    
    echo ""
    echo "Next steps:"
    echo "1. Remove old virtual environment:"
    echo "   rm -rf venv"
    echo ""
    echo "2. Create new virtual environment with Python 3.12:"
    echo "   python3.12 -m venv venv"
    echo ""
    echo "3. Run the setup script:"
    echo "   ./scripts/start.sh"
else
    echo "❌ Python 3.12 installation failed"
    echo "Please try manually:"
    echo "brew install python@3.12"
fi