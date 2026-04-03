"""Unit tests for Statistics._merge_statistics_data."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.statistics.statistics import Statistics

# normal

def test_merge_statistics_data_returns_weekly_and_seasonal_results(statistics: Statistics) -> None:
    """_merge_statistics_data returns weekly and seasonal results from the child mergers."""
    sources = {"player_weekly": pd.DataFrame(), "player_seasonal": pd.DataFrame()}
    weekly_df = pd.DataFrame([{"weekly": 1}])
    seasonal_df = pd.DataFrame([{"seasonal": 1}])

    statistics._merge_weekly_statistics_data = MagicMock(return_value=weekly_df)
    statistics._merge_seasonal_statistics_data = MagicMock(return_value=seasonal_df)

    weekly_result, seasonal_result = statistics._merge_statistics_data(sources)

    assert weekly_result is weekly_df
    assert seasonal_result is seasonal_df
    assert statistics._merge_weekly_statistics_data.call_args.args[0] is sources
    assert statistics._merge_seasonal_statistics_data.call_args.args[0] is sources

# exception

def test_merge_statistics_data_propagates_child_merge_failure(statistics: Statistics) -> None:
    """_merge_statistics_data propagates a child merge failure."""
    sources = {"player_weekly": pd.DataFrame(), "player_seasonal": pd.DataFrame()}

    def raise_error(_: dict[str, pd.DataFrame]) -> pd.DataFrame:
        raise RuntimeError("dummy")

    statistics._merge_weekly_statistics_data = raise_error
    statistics._merge_seasonal_statistics_data = MagicMock(return_value=pd.DataFrame())

    with pytest.raises(RuntimeError, match="dummy"):
        statistics._merge_statistics_data(sources)
