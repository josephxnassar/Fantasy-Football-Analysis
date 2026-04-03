"""Unit tests for App.load."""

import pytest

from backend.app import App
from backend.util import cache_keys

# normal

def test_app_load_populates_all_top_level_caches(app: App) -> None:
    """load populates the three top-level caches from the repository."""
    app.db.load_from_db.side_effect = ["DepthChart-cache", "Schedules-cache", "Statistics-cache"]

    app.load()

    assert app.caches == {
        cache_keys.CACHE["DEPTHCHART"]: "DepthChart-cache",
        cache_keys.CACHE["SCHEDULES"]: "Schedules-cache",
        cache_keys.CACHE["STATISTICS"]: "Statistics-cache",
    }

# edge

def test_app_load_overwrites_existing_caches(app: App) -> None:
    """load overwrites any previously stored top-level caches."""
    app.caches = {
        cache_keys.CACHE["DEPTHCHART"]: "old-depth",
        cache_keys.CACHE["SCHEDULES"]: "old-schedules",
        cache_keys.CACHE["STATISTICS"]: "old-statistics",
    }
    app.db.load_from_db.side_effect = ["new-DepthChart", "new-Schedules", "new-Statistics"]

    app.load()

    assert app.caches == {
        cache_keys.CACHE["DEPTHCHART"]: "new-DepthChart",
        cache_keys.CACHE["SCHEDULES"]: "new-Schedules",
        cache_keys.CACHE["STATISTICS"]: "new-Statistics",
    }

# exception

def test_app_load_propagates_repository_failure(app: App) -> None:
    """load propagates a repository failure."""
    app.db.load_from_db.side_effect = RuntimeError("dummy")

    with pytest.raises(RuntimeError, match="dummy"):
        app.load()
