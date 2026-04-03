"""Unit tests for Statistics._merge_weekly_statistics_data."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.statistics import statistics as statistics_module
from backend.statistics.statistics import Statistics

# normal

def test_merge_weekly_statistics_data_merges_all_weekly_sources(statistics: Statistics, monkeypatch: pytest.MonkeyPatch) -> None:
    """_merge_weekly_statistics_data merges the weekly sources into the base weekly frame."""
    base_df = pd.DataFrame([{"base_season": 2024, "base_week": 1, "base_player_id": "1"}])
    sources = {
        "player_weekly": base_df,
        "snap_counts": pd.DataFrame([{"base_season": 2024, "base_week": 1, "base_player_id": "1", "snap_off": 42}]),
        "ff_opp_weekly": pd.DataFrame([{"base_season": 2024, "base_week": 1, "base_player_id": "1", "rush_yds_exp": 10}]),
        "nextgen_pass_weekly": pd.DataFrame([{"base_season": 2024, "base_week": 1, "base_player_id": "1", "pass_rating": 90}]),
        "nextgen_rec_weekly": pd.DataFrame([{"base_season": 2024, "base_week": 1, "base_player_id": "1", "rec_avg_sep": 3.4}]),
        "nextgen_rush_weekly": pd.DataFrame([{"base_season": 2024, "base_week": 1, "base_player_id": "1", "rush_efficiency": 0.2}]),
        "pfr_pass_weekly": pd.DataFrame([{"base_season": 2024, "base_week": 1, "base_player_id": "1", "pass_epa": 0.1}]),
        "pfr_rush_weekly": pd.DataFrame([{"base_season": 2024, "base_week": 1, "base_player_id": "1", "rush_epa": 0.2}]),
        "pfr_rec_weekly": pd.DataFrame([{"base_season": 2024, "base_week": 1, "base_player_id": "1", "rec_epa": 0.3}]),
    }
    monkeypatch.setattr(statistics_module.stats_helpers, "apply_name_map", lambda df: df)

    merged = statistics._merge_weekly_statistics_data(sources)

    assert merged.to_dict("records") == [{
        "base_season": 2024,
        "base_week": 1,
        "base_player_id": "1",
        "snap_off": 42,
        "rush_yds_exp": 10,
        "pass_rating": 90,
        "rec_avg_sep": 3.4,
        "rush_efficiency": 0.2,
        "pass_epa": 0.1,
        "rush_epa": 0.2,
        "rec_epa": 0.3,
    }]

# edge

def test_merge_weekly_statistics_data_applies_name_map_to_each_weekly_source(statistics: Statistics, monkeypatch: pytest.MonkeyPatch) -> None:
    """_merge_weekly_statistics_data applies the name map to each weekly source in order."""
    base_df = pd.DataFrame([{"base_season": 2024, "base_week": 1, "base_player_id": "1"}])
    source_keys = [
        "snap_counts",
        "ff_opp_weekly",
        "nextgen_pass_weekly",
        "nextgen_rec_weekly",
        "nextgen_rush_weekly",
        "pfr_pass_weekly",
        "pfr_rush_weekly",
        "pfr_rec_weekly",
    ]
    sources = {"player_weekly": base_df} | {source_key: pd.DataFrame() for source_key in source_keys}
    apply_name_map_mock = MagicMock(side_effect=lambda df: df)
    monkeypatch.setattr(statistics_module.stats_helpers, "apply_name_map", apply_name_map_mock)
    monkeypatch.setattr(statistics_module.stats_helpers, "left_merge_fill", lambda base, df, join_keys: base)

    statistics._merge_weekly_statistics_data(sources)

    assert all(call.args[0] is sources[source_key] for call, source_key in zip(apply_name_map_mock.call_args_list, source_keys))

# exception

def test_merge_weekly_statistics_data_propagates_merge_failure(statistics: Statistics, monkeypatch: pytest.MonkeyPatch) -> None:
    """_merge_weekly_statistics_data propagates a helper merge failure."""
    sources = {
        "player_weekly": pd.DataFrame([{"base_season": 2024, "base_week": 1, "base_player_id": "1"}]),
        "snap_counts": pd.DataFrame(),
        "ff_opp_weekly": pd.DataFrame(),
        "nextgen_pass_weekly": pd.DataFrame(),
        "nextgen_rec_weekly": pd.DataFrame(),
        "nextgen_rush_weekly": pd.DataFrame(),
        "pfr_pass_weekly": pd.DataFrame(),
        "pfr_rush_weekly": pd.DataFrame(),
        "pfr_rec_weekly": pd.DataFrame(),
    }
    monkeypatch.setattr(statistics_module.stats_helpers, "apply_name_map", lambda df: df)

    def raise_error(base: pd.DataFrame, df: pd.DataFrame, join_keys: list[str]) -> pd.DataFrame:
        raise RuntimeError("dummy")

    monkeypatch.setattr(statistics_module.stats_helpers, "left_merge_fill", raise_error)

    with pytest.raises(RuntimeError, match="dummy"):
        statistics._merge_weekly_statistics_data(sources)
