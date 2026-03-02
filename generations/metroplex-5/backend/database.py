"""
Database connection and operations for SQLite
"""
import sqlite3
import os
from contextlib import contextmanager
from typing import Generator

DATABASE_URL = os.path.join(os.path.dirname(__file__), "ai_agent_analytics.db")

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections
    """
    conn = sqlite3.connect(DATABASE_URL)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database():
    """
    Initialize database schema with users and items tables
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id),
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index on items.user_id for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_user_id ON items(user_id)")

def seed_database() -> None:
    """
    Add seed data for development
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Check if database already has data
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        if user_count > 0:
            # Database already seeded
            return

        # Insert sample users
        users = [
            ("user-1", "Alice Johnson", "alice@example.com"),
            ("user-2", "Bob Smith", "bob@example.com"),
            ("user-3", "Charlie Davis", "charlie@example.com")
        ]

        cursor.executemany(
            "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
            users
        )

        # Insert sample items
        items = [
            ("item-1", "user-1", "Complete Project Setup", "Initialize the project structure and dependencies", "active"),
            ("item-2", "user-1", "Implement Authentication", "Add user login and registration", "active"),
            ("item-3", "user-2", "Create Dashboard", "Build analytics dashboard UI", "active"),
            ("item-4", "user-2", "API Integration", "Connect frontend to backend API", "completed"),
            ("item-5", "user-3", "Write Tests", "Add unit and integration tests", "active"),
            ("item-6", "user-3", "Deploy to Production", "Set up CI/CD pipeline", "pending")
        ]

        cursor.executemany(
            "INSERT INTO items (id, user_id, title, description, status) VALUES (?, ?, ?, ?, ?)",
            items
        )
