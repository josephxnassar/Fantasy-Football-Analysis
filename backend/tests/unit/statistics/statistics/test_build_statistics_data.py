"""Unit tests for Statistics._build_statistics_data."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.statistics.statistics import Statistics

# normal

def test_build_statistics_data_returns_payloads_and_merged_meta(statistics: Statistics) -> None:
    """_build_statistics_data returns the three payloads and merged meta."""
    statistics._build_seasonal_player_stats = MagicMock(return_value=([{"key": "seasonal"}], {"seasonal_record_count": 1}))
    statistics._build_weekly_player_stats = MagicMock(return_value=([{"key": "weekly"}], {"weekly_record_count": 2}))
    statistics._build_all_players = MagicMock(return_value=([{"key": "players"}], {"player_positions_count": 3}))

    seasonal_stats, weekly_stats, all_players, meta = statistics._build_statistics_data(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {("Jayden Daniels", "1")})

    assert seasonal_stats == [{"key": "seasonal"}]
    assert weekly_stats == [{"key": "weekly"}]
    assert all_players == [{"key": "players"}]
    assert meta == {"player_positions_count": 3, "seasonal_record_count": 1, "weekly_record_count": 2}

# exception

def test_build_statistics_data_propagates_child_builder_failure(statistics: Statistics) -> None:
    """_build_statistics_data propagates a child builder failure."""
    def raise_error(_: pd.DataFrame):
        raise RuntimeError("dummy")

    statistics._build_seasonal_player_stats = raise_error
    statistics._build_weekly_player_stats = MagicMock(return_value=([], {}))
    statistics._build_all_players = MagicMock(return_value=([], {}))

    with pytest.raises(RuntimeError, match="dummy"):
        statistics._build_statistics_data(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), set())
