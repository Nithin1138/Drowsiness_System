@echo off
REM Driver Monitoring System - Windows Startup Script
REM This script helps you start all required services

echo ========================================
echo Driver Monitoring System - Startup
echo ========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo.
    echo Please create a .env file with your Telegram bot token:
    echo   TELEGRAM_BOT_TOKEN=your_token_here
    echo.
    pause
    exit /b 1
)

echo [OK] .env file found
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if required files exist
if not exist "app.py" (
    echo [ERROR] app.py not found!
    echo Please run this script from the VIEW directory
    pause
    exit /b 1
)

if not exist "telegram_listener.py" (
    echo [ERROR] telegram_listener.py not found!
    pause
    exit /b 1
)

echo [OK] Required files found
echo.

REM Create data directory if it doesn't exist
if not exist "data" mkdir data

echo ========================================
echo Starting Services...
echo ========================================
echo.

echo Starting Telegram Listener...
echo (This will open in a new window)
start "Telegram Listener" cmd /k "python telegram_listener.py"
timeout /t 2 /nobreak >nul

echo Starting Flask Server...
echo (This will open in a new window)
start "Flask Server" cmd /k "python app.py"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo System Started Successfully!
echo ========================================
echo.
echo Two windows have been opened:
echo   1. Telegram Listener - Handles phone registration
echo   2. Flask Server - Web application
echo.
echo Next steps:
echo   1. Open browser: http://localhost:5000
echo   2. Register your phone with the Telegram bot (if not done)
echo   3. Login with OTP
echo.
echo To start detection system, run in a new terminal:
echo   python c.py
echo.
echo Press any key to exit this window...
pause >nul

