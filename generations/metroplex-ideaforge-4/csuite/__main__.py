"""Allow csuite to be run as a module with python -m csuite."""
from .main import cli

if __name__ == '__main__':
    cli()
