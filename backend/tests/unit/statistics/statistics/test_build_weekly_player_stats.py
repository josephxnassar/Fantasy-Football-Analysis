"""Unit tests for Statistics._build_weekly_player_stats."""

import pandas as pd

from backend.statistics.statistics import Statistics

# normal

def test_build_weekly_player_stats_returns_records_and_count(statistics: Statistics) -> None:
    """_build_weekly_player_stats returns flat weekly records and meta count."""
    weekly_df = pd.DataFrame([
        {"base_season": 2024, "base_week": 1, "base_player_id": "1"},
        {"base_season": 2024, "base_week": 2, "base_player_id": "1"},
    ])

    weekly_stats, weekly_meta = statistics._build_weekly_player_stats(weekly_df)

    assert weekly_stats == [
        {"base_season": 2024, "base_week": 1, "base_player_id": "1"},
        {"base_season": 2024, "base_week": 2, "base_player_id": "1"},
    ]
    assert weekly_meta == {"weekly_record_count": 2}

# edge

def test_build_weekly_player_stats_returns_empty_output_for_empty_frame(statistics: Statistics) -> None:
    """_build_weekly_player_stats returns an empty payload and zero count for an empty frame."""
    weekly_stats, weekly_meta = statistics._build_weekly_player_stats(pd.DataFrame())

    assert weekly_stats == []
    assert weekly_meta == {"weekly_record_count": 0}
