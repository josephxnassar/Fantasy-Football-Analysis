from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.app import App
from backend.database.DAO.sqlite_dao import SQLiteCacheManager
from backend.database.service.sqlite_service import SQLService
from backend.util import constants

pytestmark = pytest.mark.integration

def test_sqlite_service_round_trip_for_all_cache_families(tmp_path, stats_cache, schedules_cache, depth_chart_cache) -> None:
    db_path = tmp_path / "integration_cache.db"
    service = SQLService()
    service.db.close()
    service.db = SQLiteCacheManager(str(db_path))

    try:
        assert service.has_cached_data() is False

        service.save_to_db(stats_cache, constants.CACHE["STATISTICS"])
        service.save_to_db(schedules_cache, constants.CACHE["SCHEDULES"])
        service.save_to_db(depth_chart_cache, constants.CACHE["DEPTH_CHART"])

        assert service.has_cached_data() is True

        loaded_stats = service.load_from_db(constants.CACHE["STATISTICS"])
        loaded_schedules = service.load_from_db(constants.CACHE["SCHEDULES"])
        loaded_depth = service.load_from_db(constants.CACHE["DEPTH_CHART"])

        assert loaded_stats[constants.STATS["ALL_PLAYERS"]][0]["name"] == "Patrick Mahomes"
        retired = next(player for player in loaded_stats[constants.STATS["ALL_PLAYERS"]] if player["name"] == "Retired Veteran")
        assert retired["headshot_url"] is None
        assert retired["team"] is None
        assert 2025 in loaded_stats[constants.STATS["BY_YEAR"]]
        assert loaded_stats[constants.STATS["BY_YEAR"]][2025]["QB"].loc["Patrick Mahomes", "Pass TD"] == 32
        assert loaded_schedules[2025]["KC"].loc[2, "opponent"] == "BYE"
        assert loaded_depth["KC"].loc["QB", "starter"] == "Patrick Mahomes"
    finally:
        service.close()

def test_app_initialize_loads_from_cache_when_available(monkeypatch) -> None:
    app = App()
    try:
        monkeypatch.setattr(app.db, "has_cached_data", lambda: True)
        app.load = MagicMock()
        app.run = MagicMock()
        app.save = MagicMock()

        app.initialize()

        app.load.assert_called_once()
        app.run.assert_not_called()
        app.save.assert_not_called()
    finally:
        app.db.close()

def test_app_initialize_fetches_and_saves_when_cache_missing(monkeypatch) -> None:
    app = App()
    try:
        monkeypatch.setattr(app.db, "has_cached_data", lambda: False)
        app.load = MagicMock()
        app.run = MagicMock()
        app.save = MagicMock()

        app.initialize()

        app.run.assert_called_once()
        app.save.assert_called_once()
        app.load.assert_not_called()
    finally:
        app.db.close()


def test_has_cached_data_requires_core_statistics_tables(tmp_path) -> None:
    db_path = tmp_path / "cache_gate.db"
    service = SQLService()
    service.db.close()
    service.db = SQLiteCacheManager(str(db_path))

    stats_prefix = constants.CACHE["STATISTICS"]
    schedules_prefix = constants.CACHE["SCHEDULES"]
    depth_prefix = constants.CACHE["DEPTH_CHART"]

    try:
        # Incomplete stats family: all_players only.
        service.db.save_table(
            f"{stats_prefix}_{constants.STATS['ALL_PLAYERS']}",
            pd.DataFrame([{"name": "Patrick Mahomes", "position": "QB"}]),
            index=False,
        )
        service.db.save_table(
            f"{schedules_prefix}_2025_KC",
            pd.DataFrame([{"week": 1, "opponent": "BAL", "home_away": "HOME"}]),
            index=False,
        )
        service.db.save_table(
            f"{depth_prefix}_KC",
            pd.DataFrame([{"position": "QB", "starter": "Patrick Mahomes"}]),
            index=False,
        )
        assert service.has_cached_data() is False

        # Still incomplete without seasonal stats tables.
        service.db.save_table(
            f"{stats_prefix}_{constants.STATS['PLAYER_WEEKLY_STATS']}",
            pd.DataFrame([{"__player_key": "Patrick Mahomes", "season": 2025, "week": 1}]),
            index=False,
        )
        assert service.has_cached_data() is False

        # Ready only after at least one seasonal position table exists.
        service.db.save_table(
            f"{stats_prefix}_2025_QB",
            pd.DataFrame([{"player_display_name": "Patrick Mahomes", "Pass Yds": 4280}]),
            index=False,
        )
        assert service.has_cached_data() is True
    finally:
        service.close()


def test_load_table_safe_reraises_non_missing_table_errors() -> None:
    service = SQLService()

    class BrokenDB:
        def load_table(self, table_name: str):
            raise RuntimeError("database disk image is malformed")

        def close(self) -> None:
            return None

    service.db.close()
    service.db = BrokenDB()  # type: ignore[assignment]
    try:
        with pytest.raises(RuntimeError, match="malformed"):
            service._load_table_safe("Statistics_all_players")
    finally:
        service.close()


def test_load_table_safe_returns_none_for_missing_table() -> None:
    service = SQLService()
    service.db.close()
    service.db = SQLiteCacheManager(":memory:")
    try:
        assert service._load_table_safe("Statistics_missing_table") is None
    finally:
        service.close()
