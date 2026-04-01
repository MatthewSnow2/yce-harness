"""Data models for API-Evolve."""

from dataclasses import dataclass


@dataclass
class API:
    """Represents an API in the marketplace."""
    name: str
    description: str
    price: float


@dataclass
class Usage:
    """Represents usage tracking for an API."""
    api_name: str
    units: int


@dataclass
class Token:
    """Represents an access token for an API."""
    token: str
    api_name: str
    user: str
