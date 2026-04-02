"""Tests for MCP Server Discovery."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from claudeops.discovery import MCPRegistry


class TestMCPRegistry(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_json(self, filename, data):
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f)
        return filepath

    def _write_yaml(self, filename, content):
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath

    def test_load_single_json(self):
        self._write_json('server1.json', {'name': 'echo', 'endpoint': 'http://localhost:9000'})
        registry = MCPRegistry(self.temp_dir)
        result = registry.list_mcps()
        self.assertEqual(result, [('echo', 'http://localhost:9000')])

    def test_load_single_yaml(self):
        self._write_yaml('server1.yaml', 'name: proxy\nendpoint: http://localhost:9001')
        registry = MCPRegistry(self.temp_dir)
        result = registry.list_mcps()
        self.assertEqual(result, [('proxy', 'http://localhost:9001')])

    def test_load_multiple_files(self):
        self._write_json('server1.json', {'name': 'echo', 'endpoint': 'http://localhost:9000'})
        self._write_yaml('server2.yaml', 'name: proxy\nendpoint: http://localhost:9001')
        registry = MCPRegistry(self.temp_dir)
        result = sorted(registry.list_mcps())
        self.assertEqual(result, [('echo', 'http://localhost:9000'), ('proxy', 'http://localhost:9001')])

    def test_detect_file_removal(self):
        filepath = self._write_json('server1.json', {'name': 'echo', 'endpoint': 'http://localhost:9000'})
        self._write_yaml('server2.yaml', 'name: proxy\nendpoint: http://localhost:9001')
        registry = MCPRegistry(self.temp_dir)
        result = registry.list_mcps()
        self.assertEqual(len(result), 2)

        # Remove server1.json
        os.remove(filepath)
        result = registry.list_mcps()
        self.assertEqual(result, [('proxy', 'http://localhost:9001')])

    def test_detect_new_file(self):
        self._write_json('server1.json', {'name': 'echo', 'endpoint': 'http://localhost:9000'})
        registry = MCPRegistry(self.temp_dir)
        result = registry.list_mcps()
        self.assertEqual(len(result), 1)

        # Add a new file
        self._write_yaml('server2.yaml', 'name: proxy\nendpoint: http://localhost:9001')
        result = registry.list_mcps()
        self.assertEqual(len(result), 2)

    def test_malformed_json_ignored(self):
        # Write valid file
        self._write_json('good.json', {'name': 'echo', 'endpoint': 'http://localhost:9000'})
        # Write malformed file
        filepath = os.path.join(self.temp_dir, 'bad.json')
        with open(filepath, 'w') as f:
            f.write('{invalid json')

        registry = MCPRegistry(self.temp_dir)
        result = registry.list_mcps()
        self.assertEqual(result, [('echo', 'http://localhost:9000')])

    def test_missing_fields_ignored(self):
        self._write_json('server1.json', {'name': 'echo'})  # missing endpoint
        registry = MCPRegistry(self.temp_dir)
        result = registry.list_mcps()
        self.assertEqual(result, [])

    def test_empty_directory(self):
        registry = MCPRegistry(self.temp_dir)
        result = registry.list_mcps()
        self.assertEqual(result, [])

    def test_nonexistent_directory(self):
        registry = MCPRegistry('/tmp/nonexistent_mcp_dir_12345')
        result = registry.list_mcps()
        self.assertEqual(result, [])

    def test_yaml_with_comments(self):
        self._write_yaml('server1.yaml', '# This is a comment\nname: echo\n# Another comment\nendpoint: http://localhost:9000')
        registry = MCPRegistry(self.temp_dir)
        result = registry.list_mcps()
        self.assertEqual(result, [('echo', 'http://localhost:9000')])

    def test_empty_name_ignored(self):
        self._write_json('server1.json', {'name': '', 'endpoint': 'http://localhost:9000'})
        registry = MCPRegistry(self.temp_dir)
        result = registry.list_mcps()
        self.assertEqual(result, [])

    def test_default_mcp_dir_from_env(self):
        os.environ['CLAUDEOPS_MCP_DIR'] = self.temp_dir
        self._write_json('server1.json', {'name': 'echo', 'endpoint': 'http://localhost:9000'})
        try:
            registry = MCPRegistry()
            result = registry.list_mcps()
            self.assertEqual(result, [('echo', 'http://localhost:9000')])
        finally:
            del os.environ['CLAUDEOPS_MCP_DIR']


if __name__ == '__main__':
    unittest.main()
