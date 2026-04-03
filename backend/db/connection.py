"""Database connection helpers."""

from typing import Any

import psycopg

from backend.config.settings import get_database_url


def get_connection() -> Any:
    """Open a database connection."""
    return psycopg.connect(get_database_url())
