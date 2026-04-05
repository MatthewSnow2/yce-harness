"""CLI entry point for WorkflowHub using argparse."""

import argparse
import sys
from workflowhub.importer import import_artifacts
from workflowhub.feeder import display_feed


def cmd_import(args):
    """Handle the import command."""
    directory = args.dir
    imported, skipped, failed = import_artifacts(directory)
    print(f"Imported: {imported}, Skipped: {skipped}, Failed: {failed}")


def cmd_feed(args):
    """Handle the feed command."""
    limit = args.limit
    display_feed(limit)


def cmd_link(args):
    """Handle the link command (placeholder for Feature 3)."""
    print("Link command not yet implemented (Feature 3)")
    sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="workflowhub",
        description="Unified work artifact management"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Import command
    import_parser = subparsers.add_parser(
        "import",
        help="Import artifacts from JSON files"
    )
    import_parser.add_argument(
        "--dir",
        required=True,
        help="Directory containing JSON files to import"
    )
    import_parser.set_defaults(func=cmd_import)

    # Feed command (placeholder)
    feed_parser = subparsers.add_parser(
        "feed",
        help="Display unified feed of artifacts"
    )
    feed_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of items to display (default: 20)"
    )
    feed_parser.set_defaults(func=cmd_feed)

    # Link command (placeholder)
    link_parser = subparsers.add_parser(
        "link",
        help="Create link between two artifacts"
    )
    link_parser.add_argument(
        "--source",
        required=True,
        help="Source artifact in format TYPE:ID"
    )
    link_parser.add_argument(
        "--target",
        required=True,
        help="Target artifact in format TYPE:ID"
    )
    link_parser.set_defaults(func=cmd_link)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
