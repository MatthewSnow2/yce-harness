#!/bin/bash

set -e

echo "Setting up VoiceNotify MCP Plugin development environment..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

echo "Detected Python version: $PYTHON_VERSION"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install development dependencies
echo "Installing development dependencies..."
pip install pytest pytest-cov

# Install the package in development mode
echo "Installing voicenotify in development mode..."
pip install -e .

echo ""
echo "Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the MCP server:"
echo "  python -m voicenotify.main"
echo ""
echo "To run tests:"
echo "  pytest tests/ -v"
echo ""
