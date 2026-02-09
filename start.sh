#!/bin/bash

# Quick start script for Subtitle Translator Pro

echo "🎬 Starting Subtitle Translator Pro..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: ./install.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found. Using default settings..."
    cp .env.example .env
fi

# Start the application
echo "🚀 Starting server on http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

python app.py
