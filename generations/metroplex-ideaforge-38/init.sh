#!/bin/bash
# WorkflowHub - Development Server Initialization
# This is a CLI tool, so init.sh sets up the environment

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Set default data directory
export WORKFLOW_HUB_DATA_DIR="${WORKFLOW_HUB_DATA_DIR:-./data}"

# Create data directory if it doesn't exist
mkdir -p "$WORKFLOW_HUB_DATA_DIR"

# Create sample data files if they don't exist
if [ ! -f "$WORKFLOW_HUB_DATA_DIR/slack.json" ]; then
    echo '[{"id":"s1","type":"slack","content":"Team standup discussion","timestamp":"2024-01-15T09:00:00Z"},{"id":"s2","type":"slack","content":"Deploy v2.1 approved","timestamp":"2024-01-15T10:30:00Z"}]' > "$WORKFLOW_HUB_DATA_DIR/slack.json"
fi

if [ ! -f "$WORKFLOW_HUB_DATA_DIR/notion.json" ]; then
    echo '[{"id":"n1","type":"notion","content":"Sprint planning notes","timestamp":"2024-01-15T11:00:00Z"},{"id":"n2","type":"notion","content":"API design doc","timestamp":"2024-01-14T14:00:00Z"}]' > "$WORKFLOW_HUB_DATA_DIR/notion.json"
fi

if [ ! -f "$WORKFLOW_HUB_DATA_DIR/email.json" ]; then
    echo '[{"id":"e1","type":"email","content":"Client feedback on v2.0","timestamp":"2024-01-14T16:00:00Z"}]' > "$WORKFLOW_HUB_DATA_DIR/email.json"
fi

echo "WorkflowHub initialized. Data directory: $WORKFLOW_HUB_DATA_DIR"
echo ""
echo "Usage:"
echo "  python -m workflowhub.cli import --dir $WORKFLOW_HUB_DATA_DIR"
echo "  python -m workflowhub.cli feed"
echo "  python -m workflowhub.cli link --source slack:s1 --target notion:n1"
