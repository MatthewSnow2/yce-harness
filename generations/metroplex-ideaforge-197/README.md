# ClaudeOps

A command-line tool that gives solo developers live visibility into the performance of their Claude Code agents.

## Features

- **Live Metrics Collection** - Continuously parses agent log files for token latency, tool call count, and error rate
- **Automatic MCP Server Discovery** - Scans filesystem for MCP server definitions (JSON/YAML) and auto-registers them
- **Refreshing Terminal Dashboard** - Compact, updating terminal view refreshed every second

## Tech Stack

- Python 3.11+ (standard library only)
- No external dependencies

## Setup

```bash
# Set environment variables (optional - defaults shown)
export CLAUDEOPS_LOG_DIR=./logs
export CLAUDEOPS_MCP_DIR=./mcp

# Run the dashboard
python -m claudeops.cli

# Run in test mode (3 iterations then exit)
python -m claudeops.cli --test-mode
```

## Project Structure

```
claudeops/
├── __init__.py
├── cli.py            # argument parsing, main loop
├── metrics.py        # log parsing, MetricsStore
├── discovery.py      # MCP file scanning, MCPRegistry
├── models.py         # Metrics & MCPServer dataclasses
└── utils.py          # small helpers (ANSI clear, safe file read)
tests/
├── test_metrics.py
├── test_discovery.py
└── test_cli.py
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAUDEOPS_LOG_DIR` | `./logs` | Path to folder with Claude Code agent session logs |
| `CLAUDEOPS_MCP_DIR` | `./mcp` | Path to folder with MCP server configuration files |
