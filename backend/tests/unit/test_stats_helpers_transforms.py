import pandas as pd
import pytest

from backend.statistics.util import stats_helpers


def test_add_derived_stats_handles_zero_division() -> None:
    df = pd.DataFrame(
        {
            "receiving_yards": [100.0, 0.0],
            "receptions": [5.0, 0.0],
            "rushing_yards": [80.0, 20.0],
            "carries": [20.0, 0.0],
        }
    )

    result = stats_helpers.add_derived_stats(df)

    assert "Yds/Rec" in result.columns
    assert "Yds/Rush" in result.columns
    assert result.loc[0, "Yds/Rec"] == 20.0
    assert result.loc[1, "Yds/Rec"] == 0.0
    assert result.loc[0, "Yds/Rush"] == 4.0
    assert result.loc[1, "Yds/Rush"] == 0.0


def test_filter_regular_and_position_filters_regular_fantasy_positions() -> None:
    source = pd.DataFrame(
        {
            "game_type": ["REG", "REG", "PRE"],
            "position": ["WR", "K", "WR"],
            "team": ["LA", "WAS", "LA"],
        }
    )

    filtered = stats_helpers.filter_regular_and_position(source)

    assert filtered.shape[0] == 1
    assert filtered.iloc[0]["position"] == "WR"


def test_filter_regular_and_position_handles_missing_position_column() -> None:
    source = pd.DataFrame({"game_type": ["REG"], "team": ["LA"]})

    filtered = stats_helpers.filter_regular_and_position(source)

    assert filtered.empty


def test_select_columns_raises_for_missing_required_columns() -> None:
    source = pd.DataFrame({"season": [2025], "player_display_name": ["Puka Nacua"]})

    with pytest.raises(ValueError, match="test_source missing required columns: team, week"):
        stats_helpers.select_columns(
            source,
            {"season": "season", "week": "week", "team": "team"},
            ["season", "week", "team"],
            "test_source",
        )


def test_select_columns_warns_for_missing_optional_columns(caplog: pytest.LogCaptureFixture) -> None:
    source = pd.DataFrame({"season": [2025], "week": [1], "player_display_name": ["Puka Nacua"]})

    with caplog.at_level("WARNING"):
        selected = stats_helpers.select_columns(
            source,
            {
                "season": "season",
                "week": "week",
                "player_display_name": "player_display_name",
                "team": "team",
            },
            ["season", "week", "player_display_name"],
            "test_source",
        )

    assert list(selected.columns) == ["season", "week", "player_display_name"]
    assert "test_source missing optional columns: team" in caplog.text


def test_merge_weekly_aggregates_into_seasonal_applies_sum_and_mean_reducers() -> None:
    weekly_df = pd.DataFrame(
        {
            "season": [2025, 2025, 2025, 2024],
            "position": ["QB", "QB", "WR", "QB"],
            "player_display_name": [
                "Patrick Mahomes",
                "Patrick Mahomes",
                "JaMarr Chase",
                "Patrick Mahomes",
            ],
            "exp_fp": [18.5, 16.5, 7.0, 100.0],
            "ng_pass_passer_rating": [100.0, 80.0, float("nan"), 10.0],
            "ng_pass_avg_time_to_throw": [2.4, 2.8, float("nan"), 5.0],
            "ng_pass_att": [30, 20, 0, 99],
            "ng_rec_avg_separation": [float("nan"), float("nan"), 2.6, float("nan")],
            "ng_rec_targets": [0, 0, 10, 0],
            "sc_offense_pct": [0.9, 0.7, 0.85, 0.95],
            "sc_offense_snaps": [60, 40, 65, 70],
        }
    )

    seasonal_df = weekly_df[["season", "position", "player_display_name"]].drop_duplicates().copy()
    for col in (
        "exp_fp",
        "ng_pass_passer_rating",
        "ng_pass_avg_time_to_throw",
        "sc_offense_pct",
        "ng_rec_avg_separation",
    ):
        seasonal_df[col] = float("nan")

    merged = stats_helpers.merge_weekly_aggregates_into_seasonal(seasonal_df, weekly_df)
    qb_2025 = merged[
        (merged["season"] == 2025) & (merged["player_display_name"] == "Patrick Mahomes")
    ].iloc[0]
    wr_2025 = merged[
        (merged["season"] == 2025) & (merged["player_display_name"] == "JaMarr Chase")
    ].iloc[0]

    assert qb_2025["exp_fp"] == pytest.approx(35.0)
    assert qb_2025["ng_pass_passer_rating"] == pytest.approx(90.0)
    assert qb_2025["ng_pass_avg_time_to_throw"] == pytest.approx(2.6)
    assert qb_2025["sc_offense_pct"] == pytest.approx(0.8)
    assert wr_2025["ng_rec_avg_separation"] == pytest.approx(2.6)


def test_merge_weekly_aggregates_into_seasonal_fills_missing_values_only() -> None:
    seasonal_df = pd.DataFrame(
        {
            "season": [2025],
            "position": ["QB"],
            "player_display_name": ["Patrick Mahomes"],
            "exp_fp": [float("nan")],
            "ng_pass_passer_rating": [97.4],
            "ng_pass_avg_time_to_throw": [float("nan")],
            "sc_offense_pct": [float("nan")],
        }
    )
    weekly_df = pd.DataFrame(
        {
            "season": [2025, 2025],
            "position": ["QB", "QB"],
            "player_display_name": ["Patrick Mahomes", "Patrick Mahomes"],
            "exp_fp": [20.0, 15.0],
            "ng_pass_passer_rating": [100.0, 80.0],
            "ng_pass_avg_time_to_throw": [2.4, 2.8],
            "ng_pass_att": [30, 20],
            "sc_offense_pct": [0.9, 0.7],
            "sc_offense_snaps": [60, 40],
        }
    )

    merged = stats_helpers.merge_weekly_aggregates_into_seasonal(seasonal_df, weekly_df)
    row = merged.iloc[0]

    assert row["exp_fp"] == pytest.approx(35.0)
    assert row["ng_pass_passer_rating"] == pytest.approx(97.4)
    assert row["ng_pass_avg_time_to_throw"] == pytest.approx(2.6)
    assert row["sc_offense_pct"] == pytest.approx(0.8)


def test_merge_weekly_aggregates_into_seasonal_returns_seasonal_when_group_keys_missing() -> None:
    seasonal_df = pd.DataFrame({"season": [2025], "player_display_name": ["Patrick Mahomes"]})
    weekly_df = pd.DataFrame({"week": [1], "player_name": ["Patrick Mahomes"], "exp_fp": [20.0]})

    merged = stats_helpers.merge_weekly_aggregates_into_seasonal(seasonal_df, weekly_df)

    assert merged.equals(seasonal_df)


def test_combine_aliases_uses_first_non_null() -> None:
    df = pd.DataFrame({"fantasy_points_ppr": [100.0, float("nan")], "ffo_total_fp": [90.0, 80.0]})

    result = stats_helpers.combine_aliases(df)

    assert result.loc[0, "fp_ppr"] == 100.0
    assert result.loc[1, "fp_ppr"] == 80.0


def test_combine_aliases_skips_missing_source_columns() -> None:
    df = pd.DataFrame({"ng_pass_att": [10.0]})

    result = stats_helpers.combine_aliases(df)

    assert result.loc[0, "pass_att"] == 10.0


def test_combine_aliases_all_null_stays_nan() -> None:
    df = pd.DataFrame({"ffo_total_fp_exp": [float("nan")]})

    result = stats_helpers.combine_aliases(df)

    assert pd.isna(result.loc[0, "exp_fp"])


def test_add_group_ranks_ranks_within_groups() -> None:
    df = pd.DataFrame(
        {
            "season": [2025, 2025, 2025],
            "position": ["QB", "QB", "QB"],
            "fp_ppr": [300.0, 250.0, 350.0],
        }
    )

    result = stats_helpers.add_group_ranks(df, ["season", "position"])

    ranks = result["fp_ppr_rank"].tolist()
    assert ranks == [2, 3, 1]


def test_add_group_ranks_handles_ties() -> None:
    df = pd.DataFrame(
        {
            "season": [2025, 2025],
            "position": ["WR", "WR"],
            "rec_yds": [1200.0, 1200.0],
        }
    )

    result = stats_helpers.add_group_ranks(df, ["season", "position"])

    assert result["rec_yds_rank"].tolist() == [1, 1]


def test_add_group_ranks_skips_missing_default_metrics() -> None:
    df = pd.DataFrame({"season": [2025], "position": ["QB"], "fp_ppr": [300.0]})

    result = stats_helpers.add_group_ranks(df, ["season", "position"])

    assert "fp_ppr_rank" in result.columns
    assert "pass_att_rank" not in result.columns


def test_add_group_ranks_returns_unmodified_when_group_columns_missing() -> None:
    df = pd.DataFrame({"fp_ppr": [300.0, 280.0]})

    result = stats_helpers.add_group_ranks(df, ["season", "position"])

    assert result.equals(df)


def test_add_group_ranks_includes_touchdown_rank_metrics() -> None:
    df = pd.DataFrame(
        {
            "season": [2025, 2025],
            "position": ["QB", "QB"],
            "fp_ppr": [330.0, 290.0],
            "pass_att": [500.0, 480.0],
            "pass_yds": [4100.0, 3800.0],
            "pass_td": [35.0, 28.0],
            "rush_att": [70.0, 45.0],
            "rush_yds": [400.0, 220.0],
            "rush_td": [6.0, 2.0],
            "rec_yds": [0.0, 0.0],
            "rec_td": [0.0, 0.0],
            "targets": [0.0, 0.0],
            "exp_fp": [320.0, 275.0],
        }
    )

    result = stats_helpers.add_group_ranks(df, ["season", "position"])

    assert "pass_td_rank" in result.columns
    assert "rush_td_rank" in result.columns
    assert "rec_td_rank" in result.columns
    assert result["pass_td_rank"].tolist() == [1, 2]
    assert result["rush_td_rank"].tolist() == [1, 2]
