# CommitNarrative

A CLI tool that transforms recent Git commits into ready-to-post social media updates for building in public.

## Overview

CommitNarrative reads commit messages from a local Git repository, applies lightweight preprocessing to improve readability, and formats them into a concise narrative suitable for platforms like Twitter or LinkedIn.

**Target Audience**: Indie hackers, solo developers, and startup founders who want to share their development journey consistently.

## Tech Stack

- Python 3.11+
- click (CLI parsing)

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Generate a social post from last 5 commits
commitnarrative --repo . --count 5

# Save output to file
commitnarrative --repo . --count 3 --output post.txt

# Extract raw commit messages
commitnarrative extract --repo . --count 2
```

## Output Examples

- 1 commit: `Just update readme! #buildinpublic`
- 2 commits: `Just fix login bug and add profile! #buildinpublic`
- 3+ commits: `Just fix login bug, add profile, and update docs! #buildinpublic`

## Project Structure

```
commitnarrative/
├── __init__.py       # Package init
├── cli.py            # Click-based command interface
├── extractor.py      # Git commit retrieval and prefix stripping
└── generator.py      # Narrative composition logic
```
