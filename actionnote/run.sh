#!/bin/bash
# ActionNote MVP - Quick Start Script

echo "==================================="
echo "   ActionNote MVP - Starting...    "
echo "==================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys"
fi

echo ""
echo "==================================="
echo "   Starting ActionNote Server...   "
echo "==================================="
echo ""
echo "🌐 Access the app at: http://localhost:5000"
echo "⏹️  Press Ctrl+C to stop"
echo ""

# Run the Flask app
python app.py
