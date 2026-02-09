#!/bin/bash

# Subtitle Translator Pro - Installation Script
# This script installs all dependencies and sets up the application

echo "=========================================="
echo "🎬 Subtitle Translator Pro - Installer"
echo "=========================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
required_version="3.8"

if (( $(echo "$python_version < $required_version" | bc -l) )); then
    echo "❌ Error: Python 3.8+ is required. You have Python $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "⚠️ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip -q
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q
echo "✅ Dependencies installed"
echo ""

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads outputs templates utils
echo "✅ Directories created"
echo ""

# Copy .env.example to .env if not exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️ Please edit .env file and add your API keys!"
else
    echo "⚠️ .env file already exists"
fi
echo ""

echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file and add your API keys (optional)"
echo "2. Run: python app.py"
echo "3. Open browser: http://localhost:5000"
echo ""
echo "🚀 Enjoy translating!"
