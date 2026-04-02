"""MCP Server Discovery module - scans for MCP server configuration files."""
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple

from .models import MCPServer


class MCPRegistry:
    """Scans a directory for MCP server config files and maintains a registry."""

    def __init__(self, mcp_dir: str = None):
        if mcp_dir is None:
            mcp_dir = os.environ.get('CLAUDEOPS_MCP_DIR', './mcp')
        self.mcp_dir = Path(mcp_dir).resolve()
        self.servers: dict[str, MCPServer] = {}  # filepath -> MCPServer

    def _scan(self) -> None:
        """Scan the MCP directory for config files and update registry."""
        if not self.mcp_dir.exists() or not self.mcp_dir.is_dir():
            self.servers.clear()
            return

        current_files = set()

        # Scan for .json and .yaml files
        for ext in ('*.json', '*.yaml'):
            for filepath in self.mcp_dir.glob(ext):
                if filepath.is_symlink():
                    continue
                current_files.add(str(filepath))
                self._load_config(str(filepath))

        # Remove servers whose files no longer exist
        removed = set(self.servers.keys()) - current_files
        for filepath in removed:
            del self.servers[filepath]

    def _load_config(self, filepath: str) -> None:
        """Load a single config file and register the server."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()

            if filepath.endswith('.json'):
                data = json.loads(content)
            elif filepath.endswith('.yaml'):
                data = self._parse_simple_yaml(content)
            else:
                return

            name = data.get('name')
            endpoint = data.get('endpoint')

            if not isinstance(name, str) or not isinstance(endpoint, str):
                print(f"Warning: Malformed config {filepath}: missing name or endpoint", file=sys.stderr)
                return

            if not name.strip() or not endpoint.strip():
                print(f"Warning: Empty name or endpoint in {filepath}", file=sys.stderr)
                return

            self.servers[filepath] = MCPServer(name=name.strip(), endpoint=endpoint.strip())
        except (json.JSONDecodeError, OSError, ValueError) as e:
            print(f"Warning: Failed to load {filepath}: {e}", file=sys.stderr)

    def _parse_simple_yaml(self, content: str) -> dict:
        """Parse simple YAML (key: value format only) without external deps."""
        result = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' in line:
                key, _, value = line.partition(':')
                value = value.strip()
                # Remove surrounding quotes if present
                if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                    value = value[1:-1]
                result[key.strip()] = value
        return result

    def list_mcps(self) -> List[Tuple[str, str]]:
        """Return list of (name, endpoint) tuples for all registered servers."""
        self._scan()
        return [(server.name, server.endpoint) for server in self.servers.values()]


def main():
    """Demo: scan and list MCP servers."""
    registry = MCPRegistry()
    servers = registry.list_mcps()
    print(servers)


if __name__ == '__main__':
    main()
