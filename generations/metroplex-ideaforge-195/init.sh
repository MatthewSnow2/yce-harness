#!/bin/bash
# API-Evolve initialization script
set -e

cd "$(dirname "$0")"

# Install click if not present
pip install click 2>/dev/null || pip3 install click 2>/dev/null || echo "Please install click: pip install click"

echo "API-Evolve is a CLI tool. No server needed."
echo "Run: python -m api_evolve.main --help"
echo ""
echo "Example commands:"
echo "  python -m api_evolve.main register --name weather --desc 'Weather API' --price 0.01"
echo "  python -m api_evolve.main list"
echo "  python -m api_evolve.main usage --api weather --units 100"
echo "  python -m api_evolve.main price --api weather"
echo "  python -m api_evolve.main token --api weather --user alice"
echo "  python -m api_evolve.main check --token <token>"
