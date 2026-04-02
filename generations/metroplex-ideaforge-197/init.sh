#!/bin/bash
# ClaudeOps - Development Server Startup Script
set -e

cd "$(dirname "$0")"

# Create default directories if they don't exist
mkdir -p logs mcp

# Run the ClaudeOps dashboard in test mode
python -m claudeops.cli --test-mode
