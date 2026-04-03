"""Unit tests for Schedules._fill_bye_weeks."""

import pandas as pd
import pytest

from backend.schedules.schedules import Schedules
from backend.util.exceptions import DataProcessingError

# normal

def test_fill_bye_weeks_inserts_bye_row_for_missing_week(schedules: Schedules) -> None:
    """_fill_bye_weeks inserts a BYE row for a missing week."""
    team_schedule_df = pd.DataFrame([
        {"week": 1, "opponent": "LAR", "home_away": "HOME", "team_score": 24, "opponent_score": 17},
    ]).set_index("week")

    filled = schedules._fill_bye_weeks(team_schedule_df, total_weeks=2)

    assert filled.loc[2, "opponent"] == "BYE"
    assert pd.isna(filled.loc[2, "home_away"])

def test_fill_bye_weeks_preserves_existing_rows_in_week_order(schedules: Schedules) -> None:
    """_fill_bye_weeks keeps existing rows intact and returns weeks in order."""
    team_schedule_df = pd.DataFrame([
        {"week": 1, "opponent": "LAR", "home_away": "HOME", "team_score": 24, "opponent_score": 17},
    ]).set_index("week")

    filled = schedules._fill_bye_weeks(team_schedule_df, total_weeks=2)

    assert filled.index.tolist() == [1, 2]
    assert filled.loc[1].to_dict() == {"opponent": "LAR", "home_away": "HOME", "team_score": 24, "opponent_score": 17}

# edge

def test_fill_bye_weeks_leaves_full_schedule_unchanged(schedules: Schedules) -> None:
    """_fill_bye_weeks leaves a schedule unchanged when no weeks are missing."""
    team_schedule_df = pd.DataFrame([
        {"week": 1, "opponent": "LAR", "home_away": "HOME", "team_score": 24, "opponent_score": 17},
        {"week": 2, "opponent": "SEA", "home_away": "AWAY", "team_score": 21, "opponent_score": 28},
    ]).set_index("week")

    filled = schedules._fill_bye_weeks(team_schedule_df, total_weeks=2)

    assert filled.to_dict("index") == {
        1: {"opponent": "LAR", "home_away": "HOME", "team_score": 24, "opponent_score": 17},
        2: {"opponent": "SEA", "home_away": "AWAY", "team_score": 21, "opponent_score": 28},
    }

def test_fill_bye_weeks_fills_multiple_missing_weeks(schedules: Schedules) -> None:
    """_fill_bye_weeks inserts BYE rows for each missing week."""
    team_schedule_df = pd.DataFrame([
        {"week": 2, "opponent": "SEA", "home_away": "AWAY", "team_score": 21, "opponent_score": 28},
    ]).set_index("week")

    filled = schedules._fill_bye_weeks(team_schedule_df, total_weeks=4)

    assert filled["opponent"].tolist() == ["BYE", "SEA", "BYE", "BYE"]
    assert pd.isna(filled.loc[1, "home_away"])
    assert filled.loc[2, "home_away"] == "AWAY"
    assert pd.isna(filled.loc[3, "home_away"])
    assert pd.isna(filled.loc[4, "home_away"])

# exception

def test_fill_bye_weeks_raises_data_processing_error_for_missing_required_column(schedules: Schedules) -> None:
    """_fill_bye_weeks wraps malformed input in DataProcessingError."""
    malformed_team_schedule_df = pd.DataFrame([
        {"week": 1, "home_away": "HOME", "team_score": 24, "opponent_score": 17},
    ]).set_index("week")

    with pytest.raises(DataProcessingError, match="Failed to fill bye weeks") as exc_info:
        schedules._fill_bye_weeks(malformed_team_schedule_df, total_weeks=2)

    assert exc_info.value.source == "Schedules"
