"""Unit tests for Statistics._shape_statistics_data."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.statistics import statistics as statistics_module
from backend.statistics.statistics import Statistics

# normal

def test_shape_statistics_data_returns_ranked_weekly_and_seasonal_frames(statistics: Statistics, monkeypatch: pytest.MonkeyPatch) -> None:
    """_shape_statistics_data returns the ranked weekly and seasonal outputs."""
    weekly_df = pd.DataFrame([{"base_season": 2024}])
    seasonal_df = pd.DataFrame([{"base_season": 2024}])
    seasonal_merged_df = pd.DataFrame([{"base_season": 2024, "pass_rating": 100.0}])
    weekly_ranked_df = pd.DataFrame([{"base_season": 2024, "fantasy_fp_ppr_rank": 1}])
    seasonal_ranked_df = pd.DataFrame([{"base_season": 2024, "fantasy_fp_ppr_rank": 1}])
    merge_mock = MagicMock(return_value=seasonal_merged_df)
    rank_mock = MagicMock(side_effect=[weekly_ranked_df, seasonal_ranked_df])
    monkeypatch.setattr(statistics_module.stats_helpers, "merge_weekly_aggregates_into_seasonal", merge_mock)
    monkeypatch.setattr(statistics_module.stats_helpers, "add_group_ranks", rank_mock)

    weekly_result, seasonal_result = statistics._shape_statistics_data(weekly_df, seasonal_df)

    assert weekly_result is weekly_ranked_df
    assert seasonal_result is seasonal_ranked_df
    assert merge_mock.call_args.args[2] == ["base_season", "base_player_id"]

# edge

def test_shape_statistics_data_uses_expected_group_columns_for_ranking(statistics: Statistics, monkeypatch: pytest.MonkeyPatch) -> None:
    """_shape_statistics_data uses the expected weekly and seasonal rank group columns."""
    merge_mock = MagicMock(return_value=pd.DataFrame())
    rank_mock = MagicMock(side_effect=[pd.DataFrame(), pd.DataFrame()])
    monkeypatch.setattr(statistics_module.stats_helpers, "merge_weekly_aggregates_into_seasonal", merge_mock)
    monkeypatch.setattr(statistics_module.stats_helpers, "add_group_ranks", rank_mock)

    statistics._shape_statistics_data(pd.DataFrame(), pd.DataFrame())

    assert rank_mock.call_args_list[0].args[1] == ["base_season", "base_pos", "base_week"]
    assert rank_mock.call_args_list[1].args[1] == ["base_season", "base_pos"]
    assert "fantasy_fp_ppr" in rank_mock.call_args_list[0].args[2]

# exception

def test_shape_statistics_data_propagates_helper_failure(statistics: Statistics, monkeypatch: pytest.MonkeyPatch) -> None:
    """_shape_statistics_data propagates a helper failure."""
    def raise_error(*args, **kwargs):
        raise RuntimeError("dummy")

    monkeypatch.setattr(statistics_module.stats_helpers, "merge_weekly_aggregates_into_seasonal", raise_error)

    with pytest.raises(RuntimeError, match="dummy"):
        statistics._shape_statistics_data(pd.DataFrame(), pd.DataFrame())
