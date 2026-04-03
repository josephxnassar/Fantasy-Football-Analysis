"""Unit tests for StatisticsSourceLoader.load_ff_playerid_map."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.statistics import loaders as loaders_module
from backend.statistics.loaders import StatisticsSourceLoader
from backend.util.exceptions import DataLoadError

# normal

def test_load_ff_playerid_map_builds_expected_map(statistics_loader: StatisticsSourceLoader, monkeypatch: pytest.MonkeyPatch) -> None:
    """load_ff_playerid_map builds the expected PFR-to-player-id dict."""
    source_df = pd.DataFrame([
        {"pfr_id": "staffma01", "gsis_id": "00-0034860", "db_season": 2025},
        {"pfr_id": "danieja01", "gsis_id": "00-0039405", "db_season": 2025},
    ])
    mock_result = MagicMock()
    mock_result.to_pandas.return_value = source_df
    monkeypatch.setattr(loaders_module.nfl, "load_ff_playerids", lambda: mock_result)

    ff_playerid_map = statistics_loader.load_ff_playerid_map()

    assert ff_playerid_map == {"staffma01": "00-0034860", "danieja01": "00-0039405"}

# edge

def test_load_ff_playerid_map_drops_missing_rows_and_keeps_latest_duplicate(statistics_loader: StatisticsSourceLoader, monkeypatch: pytest.MonkeyPatch) -> None:
    """load_ff_playerid_map drops invalid rows and keeps the latest duplicate pfr_id."""
    source_df = pd.DataFrame([
        {"pfr_id": "staffma01", "gsis_id": "old-id", "db_season": 2024},
        {"pfr_id": "staffma01", "gsis_id": "new-id", "db_season": 2025},
        {"pfr_id": None, "gsis_id": "missing-pfr", "db_season": 2025},
        {"pfr_id": "danieja01", "gsis_id": None, "db_season": 2025},
    ])
    mock_result = MagicMock()
    mock_result.to_pandas.return_value = source_df
    monkeypatch.setattr(loaders_module.nfl, "load_ff_playerids", lambda: mock_result)

    ff_playerid_map = statistics_loader.load_ff_playerid_map()

    assert ff_playerid_map == {"staffma01": "new-id"}

# exception

def test_load_ff_playerid_map_raises_data_load_error_on_import_failure(statistics_loader: StatisticsSourceLoader, monkeypatch: pytest.MonkeyPatch) -> None:
    """load_ff_playerid_map wraps upstream failures in DataLoadError."""
    def raise_error() -> None:
        raise RuntimeError("dummy")

    monkeypatch.setattr(loaders_module.nfl, "load_ff_playerids", raise_error)

    with pytest.raises(DataLoadError, match="Failed to load ff_playerids map: dummy") as exc_info:
        statistics_loader.load_ff_playerid_map()

    assert exc_info.value.source == "Statistics"
