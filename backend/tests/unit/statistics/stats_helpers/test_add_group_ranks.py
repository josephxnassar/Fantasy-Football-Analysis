"""Unit tests for stats_helpers.add_group_ranks."""

import pandas as pd
import pytest

from backend.statistics.util import stats_helpers

# normal

def test_add_group_ranks_adds_descending_ranks_within_groups() -> None:
    """add_group_ranks adds descending metric ranks within each group."""
    source_df = pd.DataFrame([
        {"base_season": 2024, "base_pos": "QB", "base_week": 1, "fantasy_fp_ppr": 24},
        {"base_season": 2024, "base_pos": "QB", "base_week": 1, "fantasy_fp_ppr": 18},
    ])

    ranked = stats_helpers.add_group_ranks(source_df, ["base_season", "base_pos", "base_week"], ["fantasy_fp_ppr"])

    assert ranked["fantasy_fp_ppr_rank"].tolist() == [1, 2]

# edge

def test_add_group_ranks_uses_min_rank_for_ties_and_skips_missing_metrics() -> None:
    """add_group_ranks gives ties the same minimum rank and ignores missing metrics."""
    source_df = pd.DataFrame([
        {"base_season": 2024, "base_pos": "QB", "base_week": 1, "pass_yds": 300},
        {"base_season": 2024, "base_pos": "QB", "base_week": 1, "pass_yds": 300},
    ])

    ranked = stats_helpers.add_group_ranks(source_df, ["base_season", "base_pos", "base_week"], ["pass_yds", "missing_metric"])

    assert ranked["pass_yds_rank"].tolist() == [1, 1]
    assert "missing_metric_rank" not in ranked.columns

# exception

def test_add_group_ranks_raises_when_no_group_columns_exist() -> None:
    """add_group_ranks raises when none of the requested group columns exist."""
    source_df = pd.DataFrame([{"fantasy_fp_ppr": 24}, {"fantasy_fp_ppr": 18}])

    with pytest.raises(ValueError):
        stats_helpers.add_group_ranks(source_df, ["base_season", "base_pos", "base_week"], ["fantasy_fp_ppr"])
