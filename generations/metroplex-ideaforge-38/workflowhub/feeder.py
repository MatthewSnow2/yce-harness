"""Feed display logic for WorkflowHub (Feature 2)."""

from workflowhub.storage import get_recent_items, get_links_for_item, init_db


def format_item_line(item: dict, links: list) -> str:
    """
    Format a single item for display in the feed.

    Format: [TYPE] ID: CONTENT (TIMESTAMP)
    If links exist: [TYPE] ID: CONTENT (TIMESTAMP) → link1, link2

    Args:
        item: dict with keys: id, type, content, timestamp
        links: list of tuples (target_type, target_id)

    Returns:
        Formatted string for display
    """
    # Basic format: [TYPE] ID: CONTENT (TIMESTAMP)
    line = f"[{item['type']}] {item['id']}: {item['content']} ({item['timestamp']})"

    # Add links if present
    if links:
        link_strings = [f"{target_type}:{target_id}" for target_type, target_id in links]
        line += " → " + ", ".join(link_strings)

    return line


def display_feed(limit: int = 20) -> None:
    """
    Display the unified feed of artifacts.

    Shows items in reverse chronological order with any linked items.

    Args:
        limit: Maximum number of items to display (default: 20)
    """
    # Initialize database if needed (ensures tables exist)
    init_db()

    items = get_recent_items(limit)

    if not items:
        print("No items found")
        return

    for item in items:
        # Get links for this item
        links = get_links_for_item(item['id'], item['type'])

        # Format and print the line
        line = format_item_line(item, links)
        print(line)
