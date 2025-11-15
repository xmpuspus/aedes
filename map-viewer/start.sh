#!/bin/bash

# AEDES Map Viewer - Startup Script

echo "========================================"
echo "🛰️  AEDES Interactive Map Viewer"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Install parent AEDES package
echo "📥 Installing AEDES package..."
cd ..
pip install -q -e .
cd map-viewer

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting server on http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""
echo "========================================"
echo ""

# Start the Flask server
python backend/app.py
