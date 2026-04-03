"""Unit tests for Statistics._merge_seasonal_statistics_data."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.statistics import statistics as statistics_module
from backend.statistics.statistics import Statistics

# normal

def test_merge_seasonal_statistics_data_merges_all_seasonal_sources(statistics: Statistics, monkeypatch: pytest.MonkeyPatch) -> None:
    """_merge_seasonal_statistics_data merges the seasonal sources into the base seasonal frame."""
    base_df = pd.DataFrame([{"base_season": 2024, "base_player_id": "1"}])
    sources = {
        "player_seasonal": base_df,
        "pfr_pass_season": pd.DataFrame([{"base_season": 2024, "base_player_id": "1", "pass_epa": 0.1}]),
        "pfr_rush_season": pd.DataFrame([{"base_season": 2024, "base_player_id": "1", "rush_epa": 0.2}]),
        "pfr_rec_season": pd.DataFrame([{"base_season": 2024, "base_player_id": "1", "rec_epa": 0.3}]),
    }
    monkeypatch.setattr(statistics_module.stats_helpers, "apply_name_map", lambda df: df)

    merged = statistics._merge_seasonal_statistics_data(sources)

    assert merged.to_dict("records") == [{
        "base_season": 2024,
        "base_player_id": "1",
        "pass_epa": 0.1,
        "rush_epa": 0.2,
        "rec_epa": 0.3,
    }]

# edge

def test_merge_seasonal_statistics_data_applies_name_map_to_each_seasonal_source(statistics: Statistics, monkeypatch: pytest.MonkeyPatch) -> None:
    """_merge_seasonal_statistics_data applies the name map to each seasonal source in order."""
    base_df = pd.DataFrame([{"base_season": 2024, "base_player_id": "1"}])
    source_keys = ["pfr_pass_season", "pfr_rush_season", "pfr_rec_season"]
    sources = {"player_seasonal": base_df} | {source_key: pd.DataFrame() for source_key in source_keys}
    apply_name_map_mock = MagicMock(side_effect=lambda df: df)
    monkeypatch.setattr(statistics_module.stats_helpers, "apply_name_map", apply_name_map_mock)
    monkeypatch.setattr(statistics_module.stats_helpers, "left_merge_fill", lambda base, df, join_keys: base)

    statistics._merge_seasonal_statistics_data(sources)

    assert all(call.args[0] is sources[source_key] for call, source_key in zip(apply_name_map_mock.call_args_list, source_keys))

# exception

def test_merge_seasonal_statistics_data_propagates_merge_failure(statistics: Statistics, monkeypatch: pytest.MonkeyPatch) -> None:
    """_merge_seasonal_statistics_data propagates a helper merge failure."""
    sources = {
        "player_seasonal": pd.DataFrame([{"base_season": 2024, "base_player_id": "1"}]),
        "pfr_pass_season": pd.DataFrame(),
        "pfr_rush_season": pd.DataFrame(),
        "pfr_rec_season": pd.DataFrame(),
    }
    monkeypatch.setattr(statistics_module.stats_helpers, "apply_name_map", lambda df: df)

    def raise_error(base: pd.DataFrame, df: pd.DataFrame, join_keys: list[str]) -> pd.DataFrame:
        raise RuntimeError("dummy")

    monkeypatch.setattr(statistics_module.stats_helpers, "left_merge_fill", raise_error)

    with pytest.raises(RuntimeError, match="dummy"):
        statistics._merge_seasonal_statistics_data(sources)
