#!/bin/bash
set -e

cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
fi

# Start MCP Observability Server with demo data
echo "Starting MCP Observability Server..."
echo "Web dashboard: http://localhost:8766"
echo "MCP server: localhost:8765"
python -m src.main serve --demo
