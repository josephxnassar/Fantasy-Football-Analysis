"""Unit tests for Schedules._load_schedules."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.schedules import schedules as schedules_module
from backend.schedules.schedules import Schedules
from backend.util.exceptions import DataLoadError

# normal

def test_load_schedules_filters_selects_and_normalizes(schedules: Schedules, monkeypatch: pytest.MonkeyPatch) -> None:
    """_load_schedules keeps REG rows, selected columns, and normalized teams."""
    imported_schedule_df = pd.DataFrame([
        {"season": 2024, "week": 1, "game_type": "REG", "away_team": "LA", "home_team": "WAS", "away_score": 17, "home_score": 24},
        {"season": 2024, "week": 2, "game_type": "REG", "away_team": "OAK", "home_team": "SD", "away_score": 10, "home_score": 14},
        {"season": 2025, "week": 1, "game_type": "PRE", "away_team": "BUF", "home_team": "MIA", "away_score": 7, "home_score": 3},
    ])
    mock_result = MagicMock()
    mock_result.to_pandas.return_value = imported_schedule_df
    monkeypatch.setattr(schedules_module.nfl, "load_schedules", lambda seasons: mock_result)

    loaded = schedules._load_schedules()

    assert list(loaded.columns) == ["season", "week", "away_team", "home_team", "away_score", "home_score"]
    assert loaded.to_dict("records") == [
        {"season": 2024, "week": 1, "away_team": "LAR", "home_team": "WSH", "away_score": 17, "home_score": 24},
        {"season": 2024, "week": 2, "away_team": "LV", "home_team": "LAC", "away_score": 10, "home_score": 14},
    ]

def test_load_schedules_sets_weeks_by_season(schedules: Schedules, monkeypatch: pytest.MonkeyPatch) -> None:
    """_load_schedules stores the distinct week count for each season."""
    imported_schedule_df = pd.DataFrame([
        {"season": 2024, "week": 1, "game_type": "REG", "away_team": "LA", "home_team": "WAS", "away_score": 17, "home_score": 24},
        {"season": 2024, "week": 2, "game_type": "REG", "away_team": "OAK", "home_team": "SD", "away_score": 10, "home_score": 14},
        {"season": 2025, "week": 1, "game_type": "PRE", "away_team": "BUF", "home_team": "MIA", "away_score": 7, "home_score": 3},
    ])
    mock_result = MagicMock()
    mock_result.to_pandas.return_value = imported_schedule_df
    monkeypatch.setattr(schedules_module.nfl, "load_schedules", lambda seasons: mock_result)

    schedules._load_schedules()

    assert schedules.weeks_by_season == {2024: 2}

# edge

def test_load_schedules_counts_distinct_weeks_per_season(schedules: Schedules, monkeypatch: pytest.MonkeyPatch) -> None:
    """_load_schedules counts distinct weeks separately for each season."""
    imported_schedule_df = pd.DataFrame([
        {"season": 2024, "week": 1, "game_type": "REG", "away_team": "BAL", "home_team": "KC", "away_score": 20, "home_score": 27},
        {"season": 2024, "week": 1, "game_type": "REG", "away_team": "GB", "home_team": "PHI", "away_score": 29, "home_score": 34},
        {"season": 2024, "week": 2, "game_type": "REG", "away_team": "PIT", "home_team": "ATL", "away_score": 18, "home_score": 10},
        {"season": 2025, "week": 1, "game_type": "REG", "away_team": "BUF", "home_team": "MIA", "away_score": 7, "home_score": 3},
        {"season": 2025, "week": 3, "game_type": "REG", "away_team": "NE", "home_team": "CIN", "away_score": 16, "home_score": 10},
    ])
    mock_result = MagicMock()
    mock_result.to_pandas.return_value = imported_schedule_df
    monkeypatch.setattr(schedules_module.nfl, "load_schedules", lambda seasons: mock_result)

    schedules._load_schedules()

    assert schedules.weeks_by_season == {2024: 2, 2025: 2}

# exception

def test_load_schedules_raises_data_load_error_on_import_failure(schedules: Schedules, monkeypatch: pytest.MonkeyPatch) -> None:
    """_load_schedules wraps upstream failures in DataLoadError."""
    def raise_error(seasons: list[int]) -> None:
        raise RuntimeError("dummy")

    monkeypatch.setattr(schedules_module.nfl, "load_schedules", raise_error)

    with pytest.raises(DataLoadError, match="Failed to load schedules: dummy") as exc_info:
        schedules._load_schedules()

    assert exc_info.value.source == "Schedules"
