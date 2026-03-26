#!/bin/bash
# CommitNarrative - Development Setup Script
# This script sets up the development environment and installs the CLI tool

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
echo "Installing dependencies..."
pip install -e . 2>/dev/null || pip install click

echo ""
echo "CommitNarrative development environment is ready!"
echo "Usage: commitnarrative --help"
