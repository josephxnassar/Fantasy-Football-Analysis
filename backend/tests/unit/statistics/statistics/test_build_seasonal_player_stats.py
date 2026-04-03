"""Unit tests for Statistics._build_seasonal_player_stats."""

import pandas as pd

from backend.statistics.statistics import Statistics

# normal

def test_build_seasonal_player_stats_returns_records_and_count(statistics: Statistics) -> None:
    """_build_seasonal_player_stats returns flat seasonal records and meta count."""
    seasonal_df = pd.DataFrame([
        {"base_season": 2024, "base_player_id": "1"},
        {"base_season": 2024, "base_player_id": "2"},
    ])

    seasonal_stats, seasonal_meta = statistics._build_seasonal_player_stats(seasonal_df)

    assert seasonal_stats == [{"base_season": 2024, "base_player_id": "1"}, {"base_season": 2024, "base_player_id": "2"}]
    assert seasonal_meta == {"seasonal_record_count": 2}

# edge

def test_build_seasonal_player_stats_returns_empty_output_for_empty_frame(statistics: Statistics) -> None:
    """_build_seasonal_player_stats returns an empty payload and zero count for an empty frame."""
    seasonal_stats, seasonal_meta = statistics._build_seasonal_player_stats(pd.DataFrame())

    assert seasonal_stats == []
    assert seasonal_meta == {"seasonal_record_count": 0}
