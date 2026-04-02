"""Utility functions for ClaudeOps."""

import os
import re

_ANSI_PATTERN = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')


def safe_read(filepath):
    """Safely read a file and return its content or empty string on error."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except (OSError, IOError, UnicodeDecodeError):
        return ""


def sanitize_for_display(text: str) -> str:
    """Remove ANSI escape sequences and control characters from text."""
    text = _ANSI_PATTERN.sub('', text)
    return ''.join(c for c in text if c.isprintable() or c in '\n\t')


def clear_screen():
    """Clear the terminal screen using ANSI escape codes."""
    print('\033[2J\033[H', end='')
