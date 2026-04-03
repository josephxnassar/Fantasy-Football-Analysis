"""Unit tests for stats_helpers.left_merge_fill."""

import pandas as pd
import pytest

from backend.statistics.util import stats_helpers

# normal

def test_left_merge_fill_fills_missing_base_values_from_right_frame() -> None:
    """left_merge_fill fills missing base values from the right frame without overwriting present values."""
    base_df = pd.DataFrame([{"base_season": 2024, "base_player_id": "1", "base_team": None, "rec_tgts": 8}])
    merge_df = pd.DataFrame([{"base_season": 2024, "base_player_id": "1", "base_team": "WSH", "rec_tgts": 10, "rec_yds": 85}])

    merged = stats_helpers.left_merge_fill(base_df, merge_df, ["base_season", "base_player_id"])

    assert merged.to_dict("records") == [{"base_season": 2024, "base_player_id": "1", "base_team": "WSH", "rec_tgts": 8, "rec_yds": 85}]

# edge

def test_left_merge_fill_prefers_non_null_base_team_row_when_join_keys_exclude_team() -> None:
    """left_merge_fill keeps the non-null base_team duplicate when team is not a join key."""
    base_df = pd.DataFrame([{"base_season": 2024, "base_player_id": "1", "rec_tgts": None}])
    merge_df = pd.DataFrame([
        {"base_season": 2024, "base_player_id": "1", "base_team": None, "rec_tgts": 8},
        {"base_season": 2024, "base_player_id": "1", "base_team": "WSH", "rec_tgts": 10},
    ])

    merged = stats_helpers.left_merge_fill(base_df, merge_df, ["base_season", "base_player_id"])

    assert merged.to_dict("records") == [{"base_season": 2024, "base_player_id": "1", "rec_tgts": 10, "base_team": "WSH"}]

# exception

def test_left_merge_fill_raises_when_no_join_keys_exist() -> None:
    """left_merge_fill raises when none of the join keys are present."""
    base_df = pd.DataFrame([{"player_id": "1"}])
    merge_df = pd.DataFrame([{"other_id": "1"}])

    with pytest.raises(ValueError):
        stats_helpers.left_merge_fill(base_df, merge_df, ["base_season", "base_player_id"])
