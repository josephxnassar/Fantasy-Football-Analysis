"""Application settings."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEASONS = list(range(2018, 2026))
DEFAULT_POSITIONS = ["QB", "RB", "WR", "TE"]

load_dotenv(ROOT / ".env")

def get_database_url() -> str:
    """Return the configured database URL."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is not set.")
    return database_url

def get_seasons() -> list[int]:
    """Return configured seasons or the default range."""
    seasons = os.getenv("SEASONS")
    if not seasons:
        return DEFAULT_SEASONS
    return [int(season.strip()) for season in seasons.split(",") if season.strip()]

def get_positions() -> list[str]:
    """Return configured positions or the default list."""
    positions = os.getenv("POSITIONS")
    if not positions:
        return DEFAULT_POSITIONS
    return [position.strip() for position in positions.split(",") if position.strip()]
