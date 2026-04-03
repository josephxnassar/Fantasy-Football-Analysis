"""Unit tests for Statistics.run."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.statistics.statistics import Statistics
from backend.util.exceptions import DataProcessingError

# normal

def test_statistics_run_builds_and_sets_cache_in_expected_order(statistics: Statistics) -> None:
    """run loads import data, processes statistics, and stores cache in the expected order."""
    rosters_df = pd.DataFrame([{"player": "A"}])
    player_weekly_df = pd.DataFrame([{"weekly": 1}])
    player_seasonal_df = pd.DataFrame([{"seasonal": 1}])
    weekly_shaped_df = pd.DataFrame([{"weekly_shaped": 1}])
    seasonal_shaped_df = pd.DataFrame([{"seasonal_shaped": 1}])
    player_keys = {("Jayden Daniels", "1")}
    all_players = [{"name": "Jayden Daniels"}]
    meta = {"weekly_record_count": 1}
    seasonal_stats = [{"seasonal": "stat"}]
    weekly_stats = [{"weekly": "stat"}]
    snap_counts_df = pd.DataFrame([{"snap": 1}])

    statistics._source_loader.load_import_data = MagicMock(return_value={
        "rosters": rosters_df,
        "player_weekly": player_weekly_df,
        "player_seasonal": player_seasonal_df,
        "snap_counts": snap_counts_df,
    })
    statistics._merge_statistics_data = MagicMock(return_value=(player_weekly_df, player_seasonal_df))
    statistics._shape_statistics_data = MagicMock(return_value=(weekly_shaped_df, seasonal_shaped_df))
    statistics._collect_stats_player_keys = MagicMock(return_value=player_keys)
    statistics._build_statistics_data = MagicMock(return_value=(seasonal_stats, weekly_stats, all_players, meta))
    statistics.set_cache = MagicMock()

    statistics.run()

    merge_sources = statistics._merge_statistics_data.call_args.args[0]
    assert set(merge_sources) == {"player_weekly", "player_seasonal", "snap_counts"}
    assert merge_sources["player_weekly"] is player_weekly_df
    assert merge_sources["player_seasonal"] is player_seasonal_df
    assert merge_sources["snap_counts"] is snap_counts_df

    build_call_args = statistics._build_statistics_data.call_args.args
    assert build_call_args[0] is rosters_df
    assert build_call_args[1] is weekly_shaped_df
    assert build_call_args[2] is seasonal_shaped_df
    assert build_call_args[3] is player_keys
    assert statistics.set_cache.call_args.args[0] == [all_players, meta, seasonal_stats, weekly_stats]

# exception

def test_statistics_run_wraps_merge_and_shape_failures(statistics: Statistics) -> None:
    """run wraps merge or shape failures in DataProcessingError."""
    statistics._source_loader.load_import_data = MagicMock(return_value={
        "rosters": pd.DataFrame(),
        "player_weekly": pd.DataFrame(),
    })
    statistics._merge_statistics_data = MagicMock(side_effect=RuntimeError("dummy"))

    with pytest.raises(DataProcessingError, match="Failed to merge/shape statistics data: dummy") as exc_info:
        statistics.run()

    assert exc_info.value.source == "Statistics"

def test_statistics_run_wraps_payload_build_failures(statistics: Statistics) -> None:
    """run wraps payload-build failures in DataProcessingError."""
    statistics._source_loader.load_import_data = MagicMock(return_value={
        "rosters": pd.DataFrame(),
        "player_weekly": pd.DataFrame(),
    })
    statistics._merge_statistics_data = MagicMock(return_value=(pd.DataFrame(), pd.DataFrame()))
    statistics._shape_statistics_data = MagicMock(return_value=(pd.DataFrame(), pd.DataFrame()))
    statistics._collect_stats_player_keys = MagicMock(return_value=set())
    statistics._build_statistics_data = MagicMock(side_effect=RuntimeError("dummy"))

    with pytest.raises(DataProcessingError, match="Failed to build statistics payloads: dummy") as exc_info:
        statistics.run()

    assert exc_info.value.source == "Statistics"
