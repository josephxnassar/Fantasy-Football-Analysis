"""Database connection helpers."""

from typing import Any

def get_database_url() -> str:
    """Return the configured database URL."""
    raise NotImplementedError

def get_connection() -> Any:
    """Open a database connection."""
    raise NotImplementedError
