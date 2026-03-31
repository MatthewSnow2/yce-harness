#!/bin/bash
set -e

cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install typer pydantic

echo "Environment ready. Run commands like:"
echo "  echo 'Paris is the capital of France.' | python -m llm_citation_checker lookup"
