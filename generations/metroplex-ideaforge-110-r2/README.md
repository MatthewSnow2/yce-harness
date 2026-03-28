# LLM Citation Checker

A command-line tool that scans user-provided text for statements that can be verified against a local knowledge base and either adds citations to verified statements or flags statements that need verification.

## Tech Stack
- Python 3.11+
- typer (CLI framework)
- pydantic (data models)

## Setup

```bash
chmod +x init.sh
./init.sh
```

## Usage

```bash
# Look up a fact
echo 'Paris is the capital of France.' | python -m llm_citation_checker lookup

# Add citations to text
echo 'The Eiffel Tower is in Paris.' | python -m llm_citation_checker cite

# Generate unverified statements report
echo 'The moon is made of cheese.' | python -m llm_citation_checker report
```

## Features
1. Load Knowledge Base and Lookup Facts
2. Add Citations to Verified Statements
3. Generate Unverified Statements Report
