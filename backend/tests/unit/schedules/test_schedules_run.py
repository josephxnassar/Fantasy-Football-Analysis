"""Unit tests for Schedules.run."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.schedules.schedules import Schedules
from backend.util.exceptions import DataLoadError, DataProcessingError

# normal

def test_run_builds_expected_cache_in_helper_order(schedules: Schedules) -> None:
    """run calls the helper steps and sets the final cache."""
    loaded_schedule = object()
    combined_schedule_df = pd.DataFrame([
        {"season": 2024, "week": 1, "team": "WSH", "opponent": "LAR", "home_away": "HOME", "team_score": 24, "opponent_score": 17},
    ])
    filled_team_schedule_df = pd.DataFrame([
        {"week": 1, "opponent": "LAR", "home_away": "HOME", "team_score": 24, "opponent_score": 17},
    ]).set_index("week")

    schedules.weeks_by_season = {2024: 2}
    load_mock = MagicMock(return_value=loaded_schedule)
    combine_mock = MagicMock(return_value=combined_schedule_df)
    fill_mock = MagicMock(return_value=filled_team_schedule_df)
    set_cache_mock = MagicMock()

    schedules._load_schedules = load_mock
    schedules._create_combined_schedule = combine_mock
    schedules._fill_bye_weeks = fill_mock
    schedules.set_cache = set_cache_mock

    schedules.run()

    load_mock.assert_called_once_with()
    combine_mock.assert_called_once_with(loaded_schedule)
    assert fill_mock.call_count == 1
    assert fill_mock.call_args.args[1] == 2
    set_cache_mock.assert_called_once_with([
        {"season": 2024, "team": "WSH", "week": 1, "opponent": "LAR", "home_away": "HOME", "team_score": 24, "opponent_score": 17},
    ])

# edge

def test_run_uses_18_week_fallback_when_season_is_missing_from_weeks_by_season(schedules: Schedules) -> None:
    """run falls back to 18 weeks when a season is missing from weeks_by_season."""
    loaded_schedule = object()
    combined_schedule_df = pd.DataFrame([
        {"season": 2024, "week": 1, "team": "WSH", "opponent": "LAR", "home_away": "HOME", "team_score": 24, "opponent_score": 17},
    ])
    fill_mock = MagicMock(return_value=pd.DataFrame([
        {"week": 1, "opponent": "LAR", "home_away": "HOME", "team_score": 24, "opponent_score": 17},
    ]).set_index("week"))

    schedules.weeks_by_season = {}
    schedules._load_schedules = MagicMock(return_value=loaded_schedule)
    schedules._create_combined_schedule = MagicMock(return_value=combined_schedule_df)
    schedules._fill_bye_weeks = fill_mock
    schedules.set_cache = MagicMock()

    schedules.run()

    assert fill_mock.call_args.args[1] == 18

def test_run_skips_broken_team_group_and_keeps_other_rows(schedules: Schedules) -> None:
    """run skips a failing team group without dropping the successful group."""
    loaded_schedule = object()
    combined_schedule_df = pd.DataFrame([
        {"season": 2024, "week": 1, "team": "WSH", "opponent": "LAR", "home_away": "HOME", "team_score": 24, "opponent_score": 17},
        {"season": 2024, "week": 1, "team": "SEA", "opponent": "FAIL", "home_away": "AWAY", "team_score": 21, "opponent_score": 28},
    ])
    fill_mock = MagicMock(side_effect=[
        pd.DataFrame([{"week": 1, "opponent": "LAR", "home_away": "HOME", "team_score": 24, "opponent_score": 17}]).set_index("week"),
        RuntimeError("dummy"),
    ])
    set_cache_mock = MagicMock()

    schedules.weeks_by_season = {2024: 1}
    schedules._load_schedules = MagicMock(return_value=loaded_schedule)
    schedules._create_combined_schedule = MagicMock(return_value=combined_schedule_df)
    schedules._fill_bye_weeks = fill_mock
    schedules.set_cache = set_cache_mock

    schedules.run()

    set_cache_mock.assert_called_once_with([
        {"season": 2024, "team": "WSH", "week": 1, "opponent": "LAR", "home_away": "HOME", "team_score": 24, "opponent_score": 17},
    ])

# exception

def test_run_propagates_load_schedules_error(schedules: Schedules) -> None:
    """run propagates _load_schedules failures."""
    schedules._load_schedules = MagicMock(side_effect=DataLoadError("dummy", source="Schedules"))

    with pytest.raises(DataLoadError, match="dummy"):
        schedules.run()

def test_run_propagates_create_combined_schedule_error(schedules: Schedules) -> None:
    """run propagates _create_combined_schedule failures."""
    loaded_schedule = object()

    schedules._load_schedules = MagicMock(return_value=loaded_schedule)
    schedules._create_combined_schedule = MagicMock(side_effect=DataProcessingError("dummy", source="Schedules"))

    with pytest.raises(DataProcessingError, match="dummy"):
        schedules.run()
