"""Command-line interface for CommitNarrative."""

import sys
import click
from commitnarrative.extractor import extract_commits, strip_prefix
from commitnarrative.generator import generate_narrative


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """CommitNarrative - Transform Git commits into social media updates."""
    pass


@cli.command()
@click.option(
    "--repo",
    default=".",
    help="Path to Git repository (default: current directory)",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.option(
    "--count",
    default=5,
    help="Number of commits to extract (default: 5)",
    type=click.IntRange(min=1),
)
def extract(repo, count):
    """Extract commit messages from a Git repository.

    Retrieves the last N commit messages, strips conventional commit
    prefixes (feat:, fix:, etc.), and outputs them one per line.
    """
    try:
        messages = extract_commits(repo_path=repo, count=count)

        for message in messages:
            click.echo(message)

    except (FileNotFoundError, NotADirectoryError, ValueError, RuntimeError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


@cli.command()
@click.option(
    "--messages",
    multiple=True,
    help="Commit messages to process (can be specified multiple times)",
)
def generate(messages):
    """Generate a social narrative from commit messages.

    Takes commit messages (with or without conventional prefixes),
    strips the prefixes, and generates a build-in-public narrative.
    """
    try:
        # Strip conventional commit prefixes from all messages
        stripped_messages = [strip_prefix(msg) for msg in messages]

        # Generate the narrative
        narrative = generate_narrative(stripped_messages)

        # Output to stdout
        click.echo(narrative)

    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli()
