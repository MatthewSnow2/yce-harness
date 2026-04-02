"""Unit tests for metrics collection."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from claudeops.metrics import MetricsStore
from claudeops.models import Metrics


class TestMetricsStore(unittest.TestCase):
    """Test the MetricsStore class."""

    def setUp(self):
        """Create temporary log directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_log_line(self, filename, data):
        """Helper to write a JSON log line to a file."""
        log_file = self.log_dir / filename
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data) + '\n')

    def test_parse_single_latency(self):
        """Test parsing a single log line with token_latency_ms."""
        self._write_log_line('test.log', {'token_latency_ms': 120})

        store = MetricsStore(self.log_dir)
        metrics = store.get_metrics()

        self.assertIsInstance(metrics, Metrics)
        self.assertEqual(metrics.latency_ms, 120.0)
        self.assertEqual(metrics.calls_per_min, 0.0)
        self.assertEqual(metrics.errors, 0)

    def test_moving_average_calculation(self):
        """Test moving average with multiple latency entries."""
        self._write_log_line('test.log', {'token_latency_ms': 120})
        self._write_log_line('test.log', {'token_latency_ms': 80})
        self._write_log_line('test.log', {'token_latency_ms': 100})

        store = MetricsStore(self.log_dir)
        metrics = store.get_metrics()

        # Average of 120, 80, 100 = 300 / 3 = 100.0
        self.assertEqual(metrics.latency_ms, 100.0)

    def test_malformed_lines_handled_gracefully(self):
        """Test that malformed JSON lines are skipped without crashing."""
        log_file = self.log_dir / 'test.log'
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('not valid json\n')
            f.write('{"token_latency_ms": 150}\n')
            f.write('{"incomplete": \n')
            f.write('{"token_latency_ms": 50}\n')

        store = MetricsStore(self.log_dir)
        metrics = store.get_metrics()

        # Should only count the two valid lines
        self.assertEqual(metrics.latency_ms, 100.0)  # (150 + 50) / 2

    def test_error_counting(self):
        """Test that errors are counted properly."""
        self._write_log_line('test.log', {'error': 'Connection timeout'})
        self._write_log_line('test.log', {'error': 'Invalid response'})
        self._write_log_line('test.log', {'token_latency_ms': 100})

        store = MetricsStore(self.log_dir)
        metrics = store.get_metrics()

        self.assertEqual(metrics.errors, 2)
        self.assertEqual(metrics.latency_ms, 100.0)

    def test_tool_call_counting(self):
        """Test that tool calls are tracked."""
        self._write_log_line('test.log', {'tool_call': 'read_file'})
        self._write_log_line('test.log', {'tool_call': 'write_file'})
        self._write_log_line('test.log', {'tool_call': 'grep'})

        store = MetricsStore(self.log_dir)
        metrics = store.get_metrics()

        # Calls should be counted (3 calls within the last minute)
        self.assertEqual(metrics.calls_per_min, 3.0)

    def test_get_metrics_returns_correct_dataclass(self):
        """Test that get_metrics() returns a proper Metrics dataclass."""
        self._write_log_line('test.log', {'token_latency_ms': 200})
        self._write_log_line('test.log', {'tool_call': 'bash'})
        self._write_log_line('test.log', {'error': 'Failed'})

        store = MetricsStore(self.log_dir)
        metrics = store.get_metrics()

        self.assertIsInstance(metrics, Metrics)
        self.assertIsInstance(metrics.latency_ms, float)
        self.assertIsInstance(metrics.calls_per_min, float)
        self.assertIsInstance(metrics.errors, int)

    def test_rolling_window_max_20_entries(self):
        """Test that latency window only keeps last 20 entries."""
        # Write 25 entries
        for i in range(25):
            self._write_log_line('test.log', {'token_latency_ms': 100})

        store = MetricsStore(self.log_dir)
        metrics = store.get_metrics()

        # Should only have 20 entries in the window
        self.assertEqual(len(store.latency_window), 20)
        self.assertEqual(metrics.latency_ms, 100.0)

    def test_file_position_tracking(self):
        """Test that file positions are tracked to avoid re-reading."""
        self._write_log_line('test.log', {'token_latency_ms': 100})

        store = MetricsStore(self.log_dir)
        store.get_metrics()

        # Record initial error count
        initial_errors = store.error_count

        # Add an error to the log
        self._write_log_line('test.log', {'error': 'New error'})

        # Get metrics again - should only read the new line
        metrics = store.get_metrics()
        self.assertEqual(metrics.errors, initial_errors + 1)

    def test_multiple_log_files(self):
        """Test that multiple .log files are processed."""
        self._write_log_line('agent1.log', {'token_latency_ms': 100})
        self._write_log_line('agent2.log', {'token_latency_ms': 200})

        store = MetricsStore(self.log_dir)
        metrics = store.get_metrics()

        # Average of 100 and 200
        self.assertEqual(metrics.latency_ms, 150.0)

    def test_empty_log_directory(self):
        """Test handling of empty log directory."""
        empty_dir = self.log_dir / 'empty'
        empty_dir.mkdir()

        store = MetricsStore(empty_dir)
        metrics = store.get_metrics()

        self.assertEqual(metrics.latency_ms, 0.0)
        self.assertEqual(metrics.calls_per_min, 0.0)
        self.assertEqual(metrics.errors, 0)

    def test_nonexistent_log_directory(self):
        """Test handling of nonexistent log directory."""
        nonexistent = self.log_dir / 'does_not_exist'

        store = MetricsStore(nonexistent)
        metrics = store.get_metrics()

        # Should not crash
        self.assertEqual(metrics.latency_ms, 0.0)
        self.assertEqual(metrics.calls_per_min, 0.0)
        self.assertEqual(metrics.errors, 0)


if __name__ == '__main__':
    unittest.main()
