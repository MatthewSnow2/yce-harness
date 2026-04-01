"""Token generation and validation logic (Feature 3)."""

import secrets
from .db import get_connection, init_db


def generate_token(api_name: str, user: str) -> str:
    """
    Generate an access token for a user/API pair.

    Args:
        api_name: API name
        user: Username

    Returns:
        Success message with generated token

    Raises:
        ValueError: If API does not exist
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if API exists
        cursor.execute('SELECT name FROM apis WHERE name = ?', (api_name,))
        if cursor.fetchone() is None:
            raise ValueError(f"API '{api_name}' not found.")

        # Generate a random 16-byte hex token
        token = secrets.token_hex(16)

        # Store token in database
        cursor.execute(
            'INSERT INTO tokens (token, api_name, user) VALUES (?, ?, ?)',
            (token, api_name, user)
        )
        conn.commit()

        return f"Token generated for user {user}: {token}"
    finally:
        conn.close()


def check_token(token: str, api_name: str = None) -> str:
    """
    Validate an access token.

    Args:
        token: Token to validate
        api_name: Optional API name to check

    Returns:
        "Access granted" if valid, "Access denied" otherwise
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Look up the token
        cursor.execute('SELECT api_name FROM tokens WHERE token = ?', (token,))
        row = cursor.fetchone()

        if row is None:
            return "Access denied"

        # If api_name is provided, check it matches
        if api_name is not None and row['api_name'] != api_name:
            return "Access denied"

        return "Access granted"
    finally:
        conn.close()
