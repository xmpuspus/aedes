@echo off
REM AEDES Map Viewer - Startup Script for Windows

echo ========================================
echo 🛰️  AEDES Interactive Map Viewer
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM Install parent AEDES package
echo 📥 Installing AEDES package...
cd ..
pip install -q -e .
cd map-viewer

echo.
echo ✅ Setup complete!
echo.
echo 🚀 Starting server on http://localhost:5000
echo    Press Ctrl+C to stop
echo.
echo ========================================
echo.

REM Start the Flask server
python backend\app.py

pause
