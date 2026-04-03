"""Unit tests for Schedules._create_combined_schedule."""

import pandas as pd
import pytest

from backend.schedules.schedules import Schedules
from backend.util.exceptions import DataProcessingError

# normal

def test_create_combined_schedule_returns_expected_shape(schedules: Schedules) -> None:
    """_create_combined_schedule returns two team-facing rows with the expected columns."""
    loaded_schedule_df = pd.DataFrame([
        {"season": 2024, "week": 1, "away_team": "LAR", "home_team": "WSH", "away_score": 17, "home_score": 24},
    ])

    combined = schedules._create_combined_schedule(loaded_schedule_df)

    assert list(combined.columns) == ["season", "week", "team", "opponent", "home_away", "team_score", "opponent_score"]
    assert len(combined) == 2

def test_create_combined_schedule_maps_home_and_away_rows(schedules: Schedules) -> None:
    """_create_combined_schedule maps the home and away views of a game correctly."""
    loaded_schedule_df = pd.DataFrame([
        {"season": 2024, "week": 1, "away_team": "LAR", "home_team": "WSH", "away_score": 17, "home_score": 24},
    ])

    combined = schedules._create_combined_schedule(loaded_schedule_df)

    assert combined.to_dict("records") == [
        {"season": 2024, "week": 1, "team": "WSH", "opponent": "LAR", "home_away": "HOME", "team_score": 24, "opponent_score": 17},
        {"season": 2024, "week": 1, "team": "LAR", "opponent": "WSH", "home_away": "AWAY", "team_score": 17, "opponent_score": 24},
    ]

# edge

def test_create_combined_schedule_returns_empty_output_for_empty_input(schedules: Schedules) -> None:
    """_create_combined_schedule returns an empty output frame for an empty schedule."""
    empty_schedule_df = pd.DataFrame(columns=["season", "week", "away_team", "home_team", "away_score", "home_score"])

    combined = schedules._create_combined_schedule(empty_schedule_df)

    assert list(combined.columns) == ["season", "week", "team", "opponent", "home_away", "team_score", "opponent_score"]
    assert combined.empty

def test_create_combined_schedule_preserves_missing_scores(schedules: Schedules) -> None:
    """_create_combined_schedule carries missing scores into the team-facing rows."""
    loaded_schedule_df = pd.DataFrame([
        {"season": 2024, "week": 1, "away_team": "LAR", "home_team": "WSH", "away_score": None, "home_score": None},
    ])

    combined = schedules._create_combined_schedule(loaded_schedule_df)

    assert combined.to_dict("records") == [
        {"season": 2024, "week": 1, "team": "WSH", "opponent": "LAR", "home_away": "HOME", "team_score": None, "opponent_score": None},
        {"season": 2024, "week": 1, "team": "LAR", "opponent": "WSH", "home_away": "AWAY", "team_score": None, "opponent_score": None},
    ]

# exception

def test_create_combined_schedule_raises_data_processing_error_for_missing_required_column(schedules: Schedules) -> None:
    """_create_combined_schedule wraps malformed input in DataProcessingError."""
    malformed_schedule_df = pd.DataFrame([
        {"season": 2024, "week": 1, "away_team": "LAR", "home_team": "WSH", "away_score": 17},
    ])

    with pytest.raises(DataProcessingError, match="Failed to create combined schedule") as exc_info:
        schedules._create_combined_schedule(malformed_schedule_df)

    assert exc_info.value.source == "Schedules"
