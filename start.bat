@echo off
REM Quick start script for Windows

echo 🎬 Starting Subtitle Translator Pro...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found!
    echo Please run: install.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️ .env file not found. Using default settings...
    copy .env.example .env
)

REM Start the application
echo 🚀 Starting server on http://localhost:5000
echo Press Ctrl+C to stop
echo.

python app.py
