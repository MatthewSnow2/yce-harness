"""Usage tracking and pricing logic (stub for Feature 2)."""

from .db import get_connection, init_db


def record_usage(api_name: str, units: int) -> str:
    """
    Record usage for an API and adjust its price.

    Args:
        api_name: API name
        units: Number of units used

    Returns:
        Confirmation message

    Raises:
        ValueError: If API does not exist or units is invalid
    """
    # Validate units is positive
    if units <= 0:
        raise ValueError("Units must be a positive integer.")

    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if API exists
        cursor.execute('SELECT name, price FROM apis WHERE name = ?', (api_name,))
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"API '{api_name}' not found.")

        current_price = row['price']

        # Insert usage record
        cursor.execute(
            'INSERT INTO usage (api_name, units) VALUES (?, ?)',
            (api_name, units)
        )

        # Calculate total usage for this API
        cursor.execute(
            'SELECT SUM(units) as total FROM usage WHERE api_name = ?',
            (api_name,)
        )
        total_usage = cursor.fetchone()['total'] or 0

        # Apply pricing rule
        if total_usage > 1000:
            # Decrease price by 10%
            new_price = current_price * 0.9
        else:
            # Increase price by 5%
            new_price = current_price * 1.05

        # Clamp price between $0.001 and $1.00
        new_price = max(0.001, min(1.00, new_price))

        # Update the price in the apis table
        cursor.execute(
            'UPDATE apis SET price = ? WHERE name = ?',
            (new_price, api_name)
        )

        conn.commit()
        return f"Recorded {units} usage for API {api_name}."

    finally:
        conn.close()


def get_price_info(api_name: str) -> str:
    """
    Get current price and usage stats for an API.

    Args:
        api_name: API name

    Returns:
        Formatted string with price and usage information

    Raises:
        ValueError: If API does not exist
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if API exists and get current price
        cursor.execute('SELECT name, price FROM apis WHERE name = ?', (api_name,))
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"API '{api_name}' not found.")

        current_price = row['price']

        # Get total usage
        cursor.execute(
            'SELECT SUM(units) as total FROM usage WHERE api_name = ?',
            (api_name,)
        )
        result = cursor.fetchone()
        total_usage = result['total'] if result['total'] is not None else 0

        # Format price with meaningful precision
        # Show enough decimal places to represent the price accurately
        if current_price < 0.01:
            price_str = f"${current_price:.5f}"
        elif current_price < 0.1:
            price_str = f"${current_price:.5f}"
        else:
            price_str = f"${current_price:.2f}"

        # Remove trailing zeros but keep at least one decimal place
        if '.' in price_str:
            price_str = price_str.rstrip('0')
            if price_str.endswith('.'):
                price_str += '0'

        return f"Current price for {api_name}: {price_str} (usage: {total_usage})"

    finally:
        conn.close()
