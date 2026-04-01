"""Database connection and schema initialization."""

import sqlite3
import os
from typing import Optional


def get_db_path() -> str:
    """Get the database path from environment or use default."""
    return os.environ.get('API_EVOLVE_DB', './api_evolve.db')


def get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create apis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS apis (
            name TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')

    # Create usage table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_name TEXT NOT NULL,
            units INTEGER NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (api_name) REFERENCES apis(name)
        )
    ''')

    # Create tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            api_name TEXT NOT NULL,
            user TEXT NOT NULL,
            FOREIGN KEY (api_name) REFERENCES apis(name)
        )
    ''')

    conn.commit()
    conn.close()
