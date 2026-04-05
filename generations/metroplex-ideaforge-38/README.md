# WorkflowHub

A Python CLI tool that unifies work artifacts from Slack, Notion, Google Docs, and email into a single chronological feed.

## Features

- **Data Ingestion**: Import artifact data from JSON files into a local SQLite database
- **Unified Feed**: Display a reverse-chronological feed of all artifacts from all sources
- **Link Management**: Create bidirectional links between artifacts across tools

## Tech Stack

- Python 3.11+ (standard library only)
- SQLite for local storage
- No external dependencies

## Quick Start

```bash
# Initialize the project
bash init.sh

# Import artifacts
python -m workflowhub.cli import --dir data/

# View feed
python -m workflowhub.cli feed

# Link artifacts
python -m workflowhub.cli link --source slack:s1 --target notion:n1
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| WORKFLOW_HUB_DATA_DIR | ./data | Directory containing source JSON files and SQLite database |

## Project Structure

```
workflowhub/
├── cli.py          # CLI entry point (argparse)
├── storage.py      # SQLite database operations
├── importer.py     # JSON file import logic
├── feeder.py       # Feed display logic
├── linker.py       # Link management logic
└── tests/          # Test suite
```
