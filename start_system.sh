#!/bin/bash
# Driver Monitoring System - Linux/Mac Startup Script
# This script helps you start all required services

echo "========================================"
echo "Driver Monitoring System - Startup"
echo "========================================"
echo ""

# Check if TELEGRAM_BOT_TOKEN is set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "[ERROR] TELEGRAM_BOT_TOKEN is not set!"
    echo ""
    echo "Please set your Telegram bot token first:"
    echo "  export TELEGRAM_BOT_TOKEN=\"YOUR_TOKEN_HERE\""
    echo ""
    echo "Then run this script again:"
    echo "  ./start_system.sh"
    echo ""
    exit 1
fi

echo "[OK] TELEGRAM_BOT_TOKEN is set"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[ERROR] Python is not installed"
        echo "Please install Python 3.8+ from python.org"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

echo "[OK] Python is installed ($PYTHON_CMD)"
echo ""

# Check if required files exist
if [ ! -f "app.py" ]; then
    echo "[ERROR] app.py not found!"
    echo "Please run this script from the VIEW directory"
    exit 1
fi

if [ ! -f "telegram_listener.py" ]; then
    echo "[ERROR] telegram_listener.py not found!"
    exit 1
fi

echo "[OK] Required files found"
echo ""

# Create data directory if it doesn't exist
mkdir -p data

echo "========================================"
echo "Starting Services..."
echo "========================================"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $LISTENER_PID 2>/dev/null
    kill $FLASK_PID 2>/dev/null
    echo "Services stopped."
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Start Telegram Listener in background
echo "Starting Telegram Listener..."
$PYTHON_CMD telegram_listener.py &
LISTENER_PID=$!
echo "  PID: $LISTENER_PID"
sleep 2

# Start Flask Server in background
echo "Starting Flask Server..."
$PYTHON_CMD app.py &
FLASK_PID=$!
echo "  PID: $FLASK_PID"
sleep 2

echo ""
echo "========================================"
echo "System Started Successfully!"
echo "========================================"
echo ""
echo "Services running:"
echo "  1. Telegram Listener (PID: $LISTENER_PID)"
echo "  2. Flask Server (PID: $FLASK_PID)"
echo ""
echo "Next steps:"
echo "  1. Open browser: http://localhost:5000"
echo "  2. Register your phone with the Telegram bot (if not done)"
echo "  3. Login with OTP"
echo ""
echo "To start detection system, run in a new terminal:"
echo "  $PYTHON_CMD c.py"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Wait for processes
wait

