#!/bin/bash
# 🔥 Educational Data Scraper MCP Server Startup Script 🔥

echo "🚀 Starting Educational Data Scraper MCP Server..."
echo "License-compliant educational content extraction!"
echo ""

# Activate virtual environment if available
if [ -f "../../.venv310/Scripts/activate" ]; then
    echo "📦 Activating virtual environment..."
    source ../../.venv310/Scripts/activate
fi

# Install requirements if needed
echo "📋 Checking requirements..."
pip install -r requirements.txt

# Start the server
echo "🔥 LAUNCHING BADASS MCP SERVER!"
echo "Educational Data Scraper - License Compliant Edition"
echo ""
python server.py
