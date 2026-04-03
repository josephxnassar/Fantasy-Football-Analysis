"""Unit tests for Statistics._collect_stats_player_keys."""

import pandas as pd
import pytest

from backend.statistics.statistics import Statistics

# normal

def test_collect_stats_player_keys_collects_keys_from_weekly_and_seasonal_frames(statistics: Statistics) -> None:
    """_collect_stats_player_keys collects keys from both weekly and seasonal frames."""
    seasonal_df = pd.DataFrame([{"base_player_display_name": "Jayden Daniels", "base_player_id": "1"}])
    weekly_df = pd.DataFrame([{"base_player_display_name": "Matthew Stafford", "base_player_id": "2"}])

    player_keys = statistics._collect_stats_player_keys(seasonal_df, weekly_df)

    assert player_keys == {("Jayden Daniels", "1"), ("Matthew Stafford", "2")}

# edge

def test_collect_stats_player_keys_dedupes_and_drops_null_values(statistics: Statistics) -> None:
    """_collect_stats_player_keys dedupes repeated keys and drops null rows."""
    seasonal_df = pd.DataFrame([
        {"base_player_display_name": "Jayden Daniels", "base_player_id": "1"},
        {"base_player_display_name": "Jayden Daniels", "base_player_id": "1"},
        {"base_player_display_name": None, "base_player_id": "2"},
    ])
    weekly_df = pd.DataFrame([
        {"base_player_display_name": "Jayden Daniels", "base_player_id": "1"},
        {"base_player_display_name": "Matthew Stafford", "base_player_id": None},
    ])

    player_keys = statistics._collect_stats_player_keys(seasonal_df, weekly_df)

    assert player_keys == {("Jayden Daniels", "1")}

# exception

def test_collect_stats_player_keys_raises_for_missing_required_column(statistics: Statistics) -> None:
    """_collect_stats_player_keys raises when a required key column is missing."""
    seasonal_df = pd.DataFrame([{"base_player_display_name": "Jayden Daniels"}])
    weekly_df = pd.DataFrame([{"base_player_display_name": "Matthew Stafford", "base_player_id": "2"}])

    with pytest.raises(KeyError):
        statistics._collect_stats_player_keys(seasonal_df, weekly_df)
