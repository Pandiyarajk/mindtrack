@echo off
REM ActionNote MVP - Quick Start Script for Windows

echo ===================================
echo    ActionNote MVP - Starting...
echo ===================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo .env file not found. Creating from template...
    copy .env.example .env
    echo Please edit .env file with your API keys
)

echo.
echo ===================================
echo    Starting ActionNote Server...
echo ===================================
echo.
echo Access the app at: http://localhost:5000
echo Press Ctrl+C to stop
echo.

REM Run the Flask app
python app.py

pause
