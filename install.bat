@echo off
REM Subtitle Translator Pro - Windows Installation Script

echo ==========================================
echo 🎬 Subtitle Translator Pro - Installer
echo ==========================================
echo.

REM Check Python installation
echo 📋 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

python --version
echo ✅ Python found
echo.

REM Create virtual environment
echo 🔧 Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ⚠️ Virtual environment already exists
)
echo.

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip -q
echo ✅ pip upgraded
echo.

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt -q
echo ✅ Dependencies installed
echo.

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "templates" mkdir templates
if not exist "utils" mkdir utils
echo ✅ Directories created
echo.

REM Copy .env.example to .env if not exists
if not exist ".env" (
    echo ⚙️ Creating .env file...
    copy .env.example .env
    echo ✅ .env file created
    echo ⚠️ Please edit .env file and add your API keys!
) else (
    echo ⚠️ .env file already exists
)
echo.

echo ==========================================
echo ✅ Installation Complete!
echo ==========================================
echo.
echo 📝 Next steps:
echo 1. Edit .env file and add your API keys (optional)
echo 2. Run: python app.py
echo 3. Open browser: http://localhost:5000
echo.
echo 🚀 Enjoy translating!
echo.
pause
