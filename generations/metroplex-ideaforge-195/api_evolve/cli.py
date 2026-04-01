"""CLI command definitions."""

import click
from .register import register_api, list_apis, format_api_table
from .usage import record_usage, get_price_info


@click.group()
def cli():
    """API-Evolve: Self-optimizing API marketplace CLI."""
    pass


@cli.command('register')
@click.option('--name', required=True, help='API name (unique)')
@click.option('--desc', required=True, help='API description')
@click.option('--price', required=True, type=float, help='Initial price per usage unit')
def register_cmd(name: str, desc: str, price: float):
    """Register a new API."""
    try:
        register_api(name, desc, price)
        click.echo(f"API '{name}' registered successfully.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command('list')
def list_cmd():
    """List all registered APIs."""
    apis = list_apis()
    table = format_api_table(apis)
    click.echo(table)


@cli.command('usage')
@click.option('--api', required=True, help='API name')
@click.option('--units', required=True, type=int, help='Number of units used')
def usage_cmd(api: str, units: int):
    """Record usage for an API."""
    try:
        # Validate units at CLI level
        if units <= 0:
            raise ValueError("Units must be a positive integer.")
        message = record_usage(api, units)
        click.echo(message)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command('price')
@click.option('--api', required=True, help='API name')
def price_cmd(api: str):
    """Show current price and usage stats."""
    try:
        info = get_price_info(api)
        click.echo(info)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command('token')
@click.option('--api', required=True, help='API name')
@click.option('--user', required=True, help='Username')
def token_cmd(api: str, user: str):
    """Generate an access token (Feature 3 - not implemented yet)."""
    click.echo("Feature 3 (Token Generation) not implemented yet.")


@cli.command('check')
@click.option('--token', required=True, help='Token to validate')
@click.option('--api', help='API name (optional)')
def check_cmd(token: str, api: str):
    """Validate an access token (Feature 3 - not implemented yet)."""
    click.echo("Feature 3 (Token Validation) not implemented yet.")
