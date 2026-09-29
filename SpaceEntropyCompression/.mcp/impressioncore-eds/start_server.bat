@echo off
REM 🔥 Educational Data Scraper MCP Server Startup Script 🔥

echo 🚀 Starting Educational Data Scraper MCP Server...
echo License-compliant educational content extraction!
echo.

REM Activate virtual environment if available
if exist "..\..\venv310\Scripts\activate.bat" (
    echo 📦 Activating virtual environment...
    call "..\..\venv310\Scripts\activate.bat"
)

REM Install requirements if needed
echo 📋 Checking requirements...
pip install -r requirements.txt

REM Start the server
echo 🔥 LAUNCHING BADASS MCP SERVER!
echo Educational Data Scraper - License Compliant Edition
echo.
python server.py
