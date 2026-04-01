"""Application settings."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]

load_dotenv(ROOT / ".env")

DEFAULT_SEASONS = list(range(2018, 2026)) # 2025
DEFAULT_POSITIONS = ["QB", "RB", "WR", "TE"]
DEFAULT_API_REFRESH = False

def get_api_refresh() -> bool:
    """Return whether API startup should refresh source data."""
    refresh = os.getenv("API_REFRESH")
    if refresh is None:
        return DEFAULT_API_REFRESH
    return refresh.strip().lower() in {"true", "yes"}

def get_database_url() -> str:
    """Return the configured database URL."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is not set.")
    return database_url

def get_seasons() -> list[int]:
    """Return default seasons."""
    return DEFAULT_SEASONS

def get_positions() -> list[str]:
    """Return default positions"""
    return DEFAULT_POSITIONS
