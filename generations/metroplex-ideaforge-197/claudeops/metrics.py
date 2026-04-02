"""Live metrics collection from Claude Code agent log files."""

import json
import os
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path

from .models import Metrics


class MetricsStore:
    """Parse log files and maintain rolling metrics."""

    def __init__(self, log_dir=None):
        """Initialize metrics store with log directory."""
        if log_dir is None:
            log_dir = os.environ.get('CLAUDEOPS_LOG_DIR', './logs')
        self.log_dir = Path(log_dir).resolve()

        # Rolling window of last 20 latency values
        self.latency_window = deque(maxlen=20)

        # Tool call tracking
        self.tool_calls = deque(maxlen=1000)  # List of (timestamp, count) tuples

        # Error count
        self.error_count = 0

        # File positions to avoid re-reading entire files
        self.file_positions = {}

    def _parse_log_line(self, line):
        """Parse a single JSON log line and extract metrics.

        Returns:
            dict: Parsed data or None if line is malformed
        """
        try:
            return json.loads(line.strip())
        except (json.JSONDecodeError, ValueError):
            return None

    def _update_from_log_file(self, filepath):
        """Read new entries from a log file and update metrics."""
        try:
            # Get last read position for this file
            file_size = os.path.getsize(filepath)
            last_position = min(self.file_positions.get(filepath, 0), file_size)

            with open(filepath, 'r', encoding='utf-8') as f:
                # Seek to last position
                f.seek(last_position)

                # Read new lines
                for line in f:
                    if not line.strip():
                        continue

                    data = self._parse_log_line(line)
                    if data is None:
                        continue

                    # Extract token latency
                    if 'token_latency_ms' in data:
                        try:
                            latency = float(data['token_latency_ms'])
                            if latency >= 0:
                                self.latency_window.append(latency)
                        except (ValueError, TypeError):
                            pass

                    # Track tool calls
                    if 'tool_call' in data:
                        self.tool_calls.append((datetime.now(), 1))

                    # Count errors
                    if 'error' in data:
                        self.error_count += 1

                # Update file position
                self.file_positions[filepath] = f.tell()

        except (OSError, IOError, UnicodeDecodeError):
            pass

    def _calculate_calls_per_min(self):
        """Calculate tool calls per minute based on recent history."""
        if not self.tool_calls:
            return 0.0

        # Remove calls older than 1 minute
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        self.tool_calls = [(ts, count) for ts, count in self.tool_calls if ts > cutoff]

        # Sum up calls in the last minute
        return float(sum(count for _, count in self.tool_calls))

    def refresh(self):
        """Scan log directory and update metrics from all .log files."""
        if not self.log_dir.exists():
            return

        # Process all .log files
        for log_file in self.log_dir.glob('*.log'):
            self._update_from_log_file(str(log_file))

    def get_metrics(self):
        """Get current metrics snapshot.

        Returns:
            Metrics: Current metrics dataclass
        """
        # Refresh metrics first
        self.refresh()

        # Calculate average latency
        if self.latency_window:
            avg_latency = sum(self.latency_window) / len(self.latency_window)
        else:
            avg_latency = 0.0

        # Calculate calls per minute
        calls_per_min = self._calculate_calls_per_min()

        return Metrics(
            latency_ms=avg_latency,
            calls_per_min=calls_per_min,
            errors=self.error_count
        )


def main():
    """Demo the metrics collection."""
    log_dir = os.environ.get('CLAUDEOPS_LOG_DIR', './logs')
    store = MetricsStore(log_dir)
    metrics = store.get_metrics()
    print(f"Metrics(latency_ms={metrics.latency_ms}, calls_per_min={metrics.calls_per_min}, errors={metrics.errors})")


if __name__ == '__main__':
    main()
