"""Unit tests for stats_helpers._aggregate_weekly_metrics."""

import pandas as pd
import pytest

from backend.statistics.util import stats_helpers

# normal

def test_aggregate_weekly_metrics_sums_grouped_metrics() -> None:
    """_aggregate_weekly_metrics sums grouped weekly metrics."""
    weekly_df = pd.DataFrame([
        {"base_season": 2024, "base_player_id": "1", "base_week": 1, "pass_yds_exp": "100"},
        {"base_season": 2024, "base_player_id": "1", "base_week": 2, "pass_yds_exp": "150"},
    ])

    aggregated = stats_helpers._aggregate_weekly_metrics(weekly_df, ["base_season", "base_player_id"], ["pass_yds_exp"], "sum")

    assert aggregated.to_dict("records") == [{"base_season": 2024, "base_player_id": "1", "pass_yds_exp": 250}]

# edge

def test_aggregate_weekly_metrics_means_numeric_values_and_ignores_missing_metrics() -> None:
    """_aggregate_weekly_metrics averages numeric values and uses only available metrics."""
    weekly_df = pd.DataFrame([
        {"base_season": 2024, "base_player_id": "1", "base_week": 1, "pass_rating": "90"},
        {"base_season": 2024, "base_player_id": "1", "base_week": 2, "pass_rating": "bad"},
    ])

    aggregated = stats_helpers._aggregate_weekly_metrics(weekly_df, ["base_season", "base_player_id"], ["pass_rating", "missing_metric"], "mean")

    assert aggregated.to_dict("records") == [{"base_season": 2024, "base_player_id": "1", "pass_rating": 90.0}]

# exception

def test_aggregate_weekly_metrics_raises_for_missing_group_key() -> None:
    """_aggregate_weekly_metrics raises when a required group key is missing."""
    weekly_df = pd.DataFrame([{"base_season": 2024, "pass_yds_exp": 100}])

    with pytest.raises(KeyError):
        stats_helpers._aggregate_weekly_metrics(weekly_df, ["base_season", "base_player_id"], ["pass_yds_exp"], "sum")
