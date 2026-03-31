"""Pytest configuration and fixtures."""

import pytest
import asyncio
from pathlib import Path
import tempfile

from src.storage.database import Database
from src.config.settings import Settings


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    database = Database(db_path)
    await database.initialize()

    yield database

    await database.close()
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def test_settings():
    """Create test settings."""
    return Settings(
        mcp_observability_port=9999,
        web_dashboard_port=9998,
        db_path=Path("test.db"),
        log_level="DEBUG",
    )
