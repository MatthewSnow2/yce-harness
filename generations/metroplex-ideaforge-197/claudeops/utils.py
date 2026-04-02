"""Utility functions for ClaudeOps."""

import os


def safe_read(filepath):
    """Safely read a file and return its content or empty string on error."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except (OSError, IOError, UnicodeDecodeError):
        return ""


def clear_screen():
    """Clear the terminal screen using ANSI escape codes."""
    print('\033[2J\033[H', end='')
