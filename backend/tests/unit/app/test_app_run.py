"""Unit tests for App.run."""

from unittest.mock import MagicMock

import pytest

from backend import app as app_module
from backend.app import App
from backend.util import cache_keys

# normal

def test_app_run_calls_load_when_refresh_is_false(app: App) -> None:
    """run loads cached data and returns early when refresh is false."""
    app.load = MagicMock()
    app.save = MagicMock()

    app.run(refresh=False)

    app.load.assert_called_once_with()
    app.save.assert_not_called()

def test_app_run_refresh_builds_caches_and_primary_keys(app: App, monkeypatch: pytest.MonkeyPatch) -> None:
    """run refreshes all sources and stores the expected cache structures."""
    depth_instance = MagicMock()
    depth_instance.get_cache.return_value = [{"team": "WSH"}]
    depth_instance.get_primary_keys.return_value = ["team", "position", "position_slot"]

    schedules_instance = MagicMock()
    schedules_instance.get_cache.return_value = [{"season": 2024, "team": "WSH"}]
    schedules_instance.get_primary_keys.return_value = ["season", "team", "week"]

    statistics_instance = MagicMock()
    statistics_instance.get_cache.return_value = [["players"], {"meta": 1}, ["seasonal"], ["weekly"]]
    statistics_instance.get_primary_keys.return_value = [["name", "player_id"], ["key"], ["base_season", "base_player_id"], ["base_season", "base_week", "base_player_id"]]

    nrp_ctor = MagicMock(return_value=depth_instance)
    schedules_ctor = MagicMock(return_value=schedules_instance)
    statistics_ctor = MagicMock(return_value=statistics_instance)
    monkeypatch.setattr(app_module, "NRPDepthChart", nrp_ctor)
    monkeypatch.setattr(app_module, "Schedules", schedules_ctor)
    monkeypatch.setattr(app_module, "Statistics", statistics_ctor)
    app.save = MagicMock()

    app.run(refresh=True)

    nrp_ctor.assert_called_once_with([2024, 2025], ["QB", "RB", "WR", "TE"])
    schedules_ctor.assert_called_once_with([2024, 2025])
    statistics_ctor.assert_called_once_with([2024, 2025], ["QB", "RB", "WR", "TE"])
    depth_instance.run.assert_called_once_with()
    schedules_instance.run.assert_called_once_with()
    statistics_instance.run.assert_called_once_with()
    assert app.caches == {
        cache_keys.CACHE["DEPTHCHART"]: [{"team": "WSH"}],
        cache_keys.CACHE["SCHEDULES"]: [{"season": 2024, "team": "WSH"}],
        cache_keys.CACHE["STATISTICS"]: {
            cache_keys.STATS["ALL"]: ["players"],
            cache_keys.STATS["META"]: {"meta": 1},
            cache_keys.STATS["SEASONAL"]: ["seasonal"],
            cache_keys.STATS["WEEKLY"]: ["weekly"],
        },
    }
    assert app.primary_keys == {
        cache_keys.CACHE["DEPTHCHART"]: ["team", "position", "position_slot"],
        cache_keys.CACHE["SCHEDULES"]: ["season", "team", "week"],
        cache_keys.CACHE["STATISTICS"]: {
            cache_keys.STATS["ALL"]: ["name", "player_id"],
            cache_keys.STATS["META"]: ["key"],
            cache_keys.STATS["SEASONAL"]: ["base_season", "base_player_id"],
            cache_keys.STATS["WEEKLY"]: ["base_season", "base_week", "base_player_id"],
        },
    }
    app.save.assert_called_once_with()

# exception

def test_app_run_refresh_propagates_source_failure_and_does_not_save(app: App, monkeypatch: pytest.MonkeyPatch) -> None:
    """run refresh propagates a source failure and does not save partial results."""
    depth_instance = MagicMock()
    depth_instance.run.side_effect = RuntimeError("dummy")

    monkeypatch.setattr(app_module, "NRPDepthChart", MagicMock(return_value=depth_instance))
    monkeypatch.setattr(app_module, "Schedules", MagicMock())
    monkeypatch.setattr(app_module, "Statistics", MagicMock())
    app.save = MagicMock()

    with pytest.raises(RuntimeError, match="dummy"):
        app.run(refresh=True)

    app.save.assert_not_called()
