"""API registration and listing logic."""

import sqlite3
from typing import List
from .db import get_connection, init_db
from .models import API


def register_api(name: str, description: str, price: float) -> None:
    """
    Register a new API in the database.

    Args:
        name: Unique API name
        description: API description
        price: Initial price per usage unit

    Raises:
        ValueError: If API with the same name already exists
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'INSERT INTO apis (name, description, price) VALUES (?, ?, ?)',
            (name, description, price)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError(f"API with name '{name}' already exists.")
    finally:
        conn.close()


def list_apis() -> List[API]:
    """
    List all registered APIs.

    Returns:
        List of API objects
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT name, description, price FROM apis ORDER BY name')
    rows = cursor.fetchall()
    conn.close()

    return [API(name=row['name'], description=row['description'], price=row['price'])
            for row in rows]


def format_api_table(apis: List[API]) -> str:
    """
    Format APIs as a readable table.

    Args:
        apis: List of API objects

    Returns:
        Formatted table string
    """
    if not apis:
        return "No APIs registered yet."

    # Calculate column widths
    name_width = max(len('name'), max(len(api.name) for api in apis))
    desc_width = max(len('description'), max(len(api.description) for api in apis))
    price_width = max(len('price'), max(len(f"{api.price:.2f}") for api in apis))

    # Build table
    separator = f"+{'-' * (name_width + 2)}+{'-' * (desc_width + 2)}+{'-' * (price_width + 2)}+"
    header = f"| {'name':<{name_width}} | {'description':<{desc_width}} | {'price':<{price_width}} |"

    lines = [separator, header, separator]
    for api in apis:
        line = f"| {api.name:<{name_width}} | {api.description:<{desc_width}} | {api.price:<{price_width}.2f} |"
        lines.append(line)
    lines.append(separator)

    return '\n'.join(lines)
