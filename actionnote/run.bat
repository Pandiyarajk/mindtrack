@echo off
REM ActionNote MVP - Quick Start Script for Windows (Local Python)

echo ===================================
echo    ActionNote MVP - Starting...
echo ===================================
echo.

REM Install dependencies using local Python
echo Installing dependencies...
python -m pip install -r requirements.txt

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
