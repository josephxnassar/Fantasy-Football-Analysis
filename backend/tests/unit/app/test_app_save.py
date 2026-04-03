"""Unit tests for App.save."""

import pytest

from backend.app import App
from backend.util import cache_keys

# normal

def test_app_save_persists_each_cache_with_matching_primary_keys(app: App) -> None:
    """save persists each cache with the matching primary keys."""
    app.caches = {
        cache_keys.CACHE["DEPTHCHART"]: [{"team": "WSH"}],
        cache_keys.CACHE["SCHEDULES"]: [{"season": 2024, "team": "WSH"}],
        cache_keys.CACHE["STATISTICS"]: {cache_keys.STATS["ALL"]: ["players"]},
    }
    app.primary_keys = {
        cache_keys.CACHE["DEPTHCHART"]: ["team", "position", "position_slot"],
        cache_keys.CACHE["SCHEDULES"]: ["season", "team", "week"],
        cache_keys.CACHE["STATISTICS"]: {cache_keys.STATS["ALL"]: ["name", "player_id"]},
    }

    app.save()

    assert app.db.save_to_db.call_args_list[0].args == (cache_keys.CACHE["DEPTHCHART"], [{"team": "WSH"}], ["team", "position", "position_slot"])
    assert app.db.save_to_db.call_args_list[1].args == (cache_keys.CACHE["SCHEDULES"], [{"season": 2024, "team": "WSH"}], ["season", "team", "week"])
    assert app.db.save_to_db.call_args_list[2].args == (cache_keys.CACHE["STATISTICS"], {cache_keys.STATS["ALL"]: ["players"]}, {cache_keys.STATS["ALL"]: ["name", "player_id"]})

# edge

def test_app_save_skips_repository_calls_when_no_caches_exist(app: App) -> None:
    """save makes no repository calls when there are no caches."""
    app.save()

    app.db.save_to_db.assert_not_called()

# exception

def test_app_save_propagates_repository_failure(app: App) -> None:
    """save propagates a repository failure."""
    app.caches = {cache_keys.CACHE["DEPTHCHART"]: [{"team": "WSH"}]}
    app.primary_keys = {cache_keys.CACHE["DEPTHCHART"]: ["team", "position", "position_slot"]}
    app.db.save_to_db.side_effect = RuntimeError("dummy")

    with pytest.raises(RuntimeError, match="dummy"):
        app.save()
