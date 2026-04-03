"""Unit tests for stats_helpers.merge_weekly_aggregates_into_seasonal."""

import pandas as pd
import pytest

from backend.statistics.util import stats_helpers

# normal

def test_merge_weekly_aggregates_into_seasonal_merges_sums_and_means() -> None:
    """merge_weekly_aggregates_into_seasonal merges grouped sums and means into seasonal rows."""
    seasonal_df = pd.DataFrame([{"base_season": 2024, "base_player_id": "1", "pass_yds_exp": None, "pass_rating": None}])
    weekly_df = pd.DataFrame([
        {"base_season": 2024, "base_player_id": "1", "base_week": 1, "pass_yds_exp": 100, "pass_rating": 90},
        {"base_season": 2024, "base_player_id": "1", "base_week": 2, "pass_yds_exp": 150, "pass_rating": 110},
    ])

    merged = stats_helpers.merge_weekly_aggregates_into_seasonal(seasonal_df, weekly_df, ["base_season", "base_player_id"], ["pass_yds_exp"], ["pass_rating"])

    assert merged.to_dict("records") == [{"base_season": 2024, "base_player_id": "1", "pass_yds_exp": 250.0, "pass_rating": 100.0}]

# edge

def test_merge_weekly_aggregates_into_seasonal_keeps_existing_seasonal_values() -> None:
    """merge_weekly_aggregates_into_seasonal keeps existing seasonal values when they are already present."""
    seasonal_df = pd.DataFrame([{"base_season": 2024, "base_player_id": "1", "pass_yds_exp": 300.0, "pass_rating": None}])
    weekly_df = pd.DataFrame([
        {"base_season": 2024, "base_player_id": "1", "base_week": 1, "pass_yds_exp": 100, "pass_rating": 90},
        {"base_season": 2024, "base_player_id": "1", "base_week": 2, "pass_yds_exp": 150, "pass_rating": 110},
    ])

    merged = stats_helpers.merge_weekly_aggregates_into_seasonal(seasonal_df, weekly_df, ["base_season", "base_player_id"], ["pass_yds_exp"], ["pass_rating"])

    assert merged.to_dict("records") == [{"base_season": 2024, "base_player_id": "1", "pass_yds_exp": 300.0, "pass_rating": 100.0}]

# exception

def test_merge_weekly_aggregates_into_seasonal_raises_for_missing_group_key() -> None:
    """merge_weekly_aggregates_into_seasonal raises when a required group key is missing."""
    seasonal_df = pd.DataFrame([{"base_season": 2024, "base_player_id": "1"}])
    weekly_df = pd.DataFrame([{"base_season": 2024, "base_week": 1, "pass_yds_exp": 100}])

    with pytest.raises(KeyError):
        stats_helpers.merge_weekly_aggregates_into_seasonal(seasonal_df, weekly_df, ["base_season", "base_player_id"], ["pass_yds_exp"], [])
