"""SQLite storage operations for WorkflowHub."""

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple


def get_db_path() -> Path:
    """Get the path to the SQLite database file."""
    data_dir = os.environ.get("WORKFLOW_HUB_DATA_DIR", "./data")
    db_dir = Path(data_dir)
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "workflowhub.db"


def get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create items table with composite primary key (id, type)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT NOT NULL,
            type TEXT NOT NULL,
            content TEXT,
            timestamp TEXT NOT NULL,
            PRIMARY KEY (id, type)
        )
    """)

    # Create links table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            source_id TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_id TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def insert_item(item_id: str, item_type: str, content: str, timestamp: str) -> bool:
    """
    Insert an item into the database.

    Returns True if inserted, False if already exists (duplicate).
    Raises exception if insertion fails for other reasons.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO items (id, type, content, timestamp)
            VALUES (?, ?, ?, ?)
        """, (item_id, item_type, content, timestamp))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Duplicate entry (id, type) already exists
        return False
    finally:
        conn.close()


def item_exists(item_id: str, item_type: str) -> bool:
    """Check if an item exists in the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM items WHERE id = ? AND type = ?
    """, (item_id, item_type))

    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def get_recent_items(limit: int = 20) -> List[dict]:
    """
    Get recent items from the database, ordered by timestamp descending.

    Returns list of dicts with keys: id, type, content, timestamp
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, type, content, timestamp
        FROM items
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))

    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items


def add_link(source_type: str, source_id: str, target_type: str, target_id: str) -> None:
    """
    Add a bidirectional link between two items.

    Stores both directions for easy querying.
    """
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()

    # Insert both directions
    cursor.execute("""
        INSERT INTO links (source_type, source_id, target_type, target_id, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (source_type, source_id, target_type, target_id, created_at))

    cursor.execute("""
        INSERT INTO links (source_type, source_id, target_type, target_id, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (target_type, target_id, source_type, source_id, created_at))

    conn.commit()
    conn.close()


def get_links_for_item(item_id: str, item_type: str) -> List[Tuple[str, str]]:
    """
    Get all links for a specific item.

    Returns list of tuples: (target_type, target_id)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT target_type, target_id
        FROM links
        WHERE source_type = ? AND source_id = ?
    """, (item_type, item_id))

    links = [(row['target_type'], row['target_id']) for row in cursor.fetchall()]
    conn.close()
    return links


def link_exists(source_type: str, source_id: str, target_type: str, target_id: str) -> bool:
    """
    Check if a link already exists between two items.

    Returns True if link exists in either direction.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check both directions
    cursor.execute("""
        SELECT 1 FROM links
        WHERE (source_type = ? AND source_id = ? AND target_type = ? AND target_id = ?)
           OR (source_type = ? AND source_id = ? AND target_type = ? AND target_id = ?)
    """, (source_type, source_id, target_type, target_id,
          target_type, target_id, source_type, source_id))

    exists = cursor.fetchone() is not None
    conn.close()
    return exists
