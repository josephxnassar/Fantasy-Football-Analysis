import pandas as pd
import pytest

from backend.statistics.util import stats_helpers

pytestmark = pytest.mark.unit

def test_add_derived_stats_handles_zero_division() -> None:
    df = pd.DataFrame({"receiving_yards": [100.0, 0.0],
                       "receptions": [5.0, 0.0],
                       "rushing_yards": [80.0, 20.0],
                       "carries": [20.0, 0.0]})

    result = stats_helpers.add_derived_stats(df)

    assert "Yds/Rec" in result.columns
    assert "Yds/Rush" in result.columns
    assert result.loc[0, "Yds/Rec"] == 20.0
    assert result.loc[1, "Yds/Rec"] == 0.0
    assert result.loc[0, "Yds/Rush"] == 4.0
    assert result.loc[1, "Yds/Rush"] == 0.0

def test_build_weekly_season_rollups_aggregates_with_expected_reducers() -> None:
    weekly_df = pd.DataFrame({
        "season": [2025, 2025, 2025, 2024],
        "position": ["QB", "QB", "WR", "QB"],
        "player_display_name": ["Patrick Mahomes", "Patrick Mahomes", "JaMarr Chase", "Patrick Mahomes"],
        "exp_fp": [18.5, 16.5, 7.0, 100.0],
        "ng_pass_passer_rating": [100.0, 80.0, float("nan"), 10.0],
        "ng_pass_avg_time_to_throw": [2.4, 2.8, float("nan"), 5.0],
        "ng_pass_att": [30, 20, 0, 99],
        "ng_rec_avg_separation": [float("nan"), float("nan"), 2.6, float("nan")],
        "ng_rec_targets": [0, 0, 10, 0],
    })

    rollups = stats_helpers.build_weekly_season_rollups(weekly_df)
    qb_2025 = rollups[(rollups["season"] == 2025) & (rollups["player_display_name"] == "Patrick Mahomes")].iloc[0]
    wr_2025 = rollups[(rollups["season"] == 2025) & (rollups["player_display_name"] == "JaMarr Chase")].iloc[0]

    assert qb_2025["exp_fp"] == pytest.approx(35.0)
    assert qb_2025["ng_pass_passer_rating"] == pytest.approx(92.0)
    assert qb_2025["ng_pass_avg_time_to_throw"] == pytest.approx(2.56)
    assert wr_2025["ng_rec_avg_separation"] == pytest.approx(2.6)

def test_merge_weekly_rollups_into_seasonal_fills_missing_values_only() -> None:
    seasonal_df = pd.DataFrame({
        "season": [2025],
        "position": ["QB"],
        "player_display_name": ["Patrick Mahomes"],
        "exp_fp": [float("nan")],
        "ng_pass_passer_rating": [97.4],
        "ng_pass_avg_time_to_throw": [float("nan")],
    })
    weekly_df = pd.DataFrame({
        "season": [2025, 2025],
        "position": ["QB", "QB"],
        "player_display_name": ["Patrick Mahomes", "Patrick Mahomes"],
        "exp_fp": [20.0, 15.0],
        "ng_pass_passer_rating": [100.0, 80.0],
        "ng_pass_avg_time_to_throw": [2.4, 2.8],
        "ng_pass_att": [30, 20],
    })

    merged = stats_helpers.merge_weekly_rollups_into_seasonal(seasonal_df, weekly_df)
    row = merged.iloc[0]

    assert row["exp_fp"] == pytest.approx(35.0)
    assert row["ng_pass_passer_rating"] == pytest.approx(97.4)
    assert row["ng_pass_avg_time_to_throw"] == pytest.approx(2.56)

def test_build_all_players_includes_expected_fields() -> None:
    positions = {"A": "QB", "B": "WR"}
    eligible = {"A"}
    ages = {"A": 28, "B": 24}
    headshots = {"A": "https://img/a.png"}
    teams = {"A": "KC", "B": "CIN"}
    rookies = {"B": True}

    players = stats_helpers.build_all_players(positions, eligible, ages, headshots, teams, rookies)

    by_name = {player["name"]: player for player in players}
    assert set(by_name) == {"A", "B"}
    assert by_name["A"]["is_eligible"] is True
    assert by_name["B"]["is_eligible"] is False
    assert by_name["B"]["is_rookie"] is True
    assert by_name["A"]["team"] == "KC"

def test_collect_stats_player_names_and_filter_all_players() -> None:
    seasonal_data = {
        2024: {
            "RB": pd.DataFrame({"rush_yds": [100.0]}, index=pd.Index(["Kenneth Walker III"], name="player_display_name"))
        }
    }
    weekly_stats = {"Kenneth Walker III": [{"week": 1, "rush_yds": 64.0}]}

    names = stats_helpers.collect_stats_player_names(seasonal_data, weekly_stats)
    assert names == {"Kenneth Walker III"}

    players = stats_helpers.build_all_players(player_positions={"Kenneth Walker": "RB", "Kenneth Walker III": "RB"},
                                              eligible_players={"Kenneth Walker", "Kenneth Walker III"},
                                              player_ages={"Kenneth Walker": 23, "Kenneth Walker III": 24},
                                              player_headshots={},
                                              player_teams={},
                                              player_rookies={},
                                              valid_player_names=names)
    assert [player["name"] for player in players] == ["Kenneth Walker III"]

def test_build_seasonal_data_replaces_nan_values_for_json_safety() -> None:
    seasonal_df = pd.DataFrame({
        "season": [2025],
        "position": ["WR"],
        "player_display_name": ["Test Receiver"],
        "team": [pd.NA],
        "receiving_epa": [float("nan")],
        "receiving_yards": [120.0],
    })

    seasonal_data = stats_helpers.build_seasonal_data(seasonal_df)
    row = seasonal_data[2025]["WR"].loc["Test Receiver"]
    assert row["receiving_epa"] == 0.0
    assert row["team"] is None

def test_build_weekly_player_stats_replaces_nan_values_for_json_safety() -> None:
    weekly_df = pd.DataFrame({
        "season": [2025],
        "week": [1],
        "player_display_name": ["Test Receiver"],
        "receiving_epa": [float("nan")],
        "target_share": [0.2],
    })

    weekly = stats_helpers.build_weekly_player_stats(weekly_df)
    record = weekly["Test Receiver"][0]
    assert record["receiving_epa"] is None
    assert record["target_share"] == 0.2

# --- align_pfr_seasonal_names ---

def test_align_pfr_seasonal_names_maps_short_to_full_names() -> None:
    base_df = pd.DataFrame({"player_display_name": ["Patrick Mahomes II", "Travis Kelce"]})
    pfr_df = pd.DataFrame({"player_display_name": ["Patrick Mahomes", "Travis Kelce"], "pfr_stat": [10, 20]})

    aligned = stats_helpers.align_pfr_seasonal_names(pfr_df, base_df)

    assert list(aligned["player_display_name"]) == ["Patrick Mahomes II", "Travis Kelce"]
    assert list(aligned["pfr_stat"]) == [10, 20]

def test_align_pfr_seasonal_names_strips_suffixes() -> None:
    base_df = pd.DataFrame({"player_display_name": ["Kenneth Walker III", "Marvin Harrison Jr"]})
    pfr_df = pd.DataFrame({"player_display_name": ["Kenneth Walker", "Marvin Harrison"], "yards": [80, 120]})

    aligned = stats_helpers.align_pfr_seasonal_names(pfr_df, base_df)

    assert set(aligned["player_display_name"]) == {"Kenneth Walker III", "Marvin Harrison Jr"}

def test_align_pfr_seasonal_names_passes_through_unmatched() -> None:
    base_df = pd.DataFrame({"player_display_name": ["Patrick Mahomes"]})
    pfr_df = pd.DataFrame({"player_display_name": ["Unknown Player", "Patrick Mahomes"], "stat": [5, 10]})

    aligned = stats_helpers.align_pfr_seasonal_names(pfr_df, base_df)

    assert list(aligned["player_display_name"]) == ["Unknown Player", "Patrick Mahomes"]

# --- resolve_metric_sources ---

def test_resolve_metric_sources_uses_first_non_null() -> None:
    df = pd.DataFrame({"primary": [100.0, float("nan")], "fallback": [90.0, 80.0]})
    metric_sources = {"out_col": ["primary", "fallback"]}

    result = stats_helpers.resolve_metric_sources(df, metric_sources)

    assert result.loc[0, "out_col"] == 100.0
    assert result.loc[1, "out_col"] == 80.0

def test_resolve_metric_sources_skips_missing_source_columns() -> None:
    df = pd.DataFrame({"col_a": [10.0]})
    metric_sources = {"out": ["missing_col", "col_a"]}

    result = stats_helpers.resolve_metric_sources(df, metric_sources)

    assert result.loc[0, "out"] == 10.0

def test_resolve_metric_sources_all_null_stays_nan() -> None:
    df = pd.DataFrame({"src": [float("nan")]})
    metric_sources = {"out": ["src"]}

    result = stats_helpers.resolve_metric_sources(df, metric_sources)

    assert pd.isna(result.loc[0, "out"])

# --- add_group_ranks ---

def test_add_group_ranks_ranks_within_groups() -> None:
    df = pd.DataFrame({
        "season": [2025, 2025, 2025],
        "position": ["QB", "QB", "QB"],
        "fp_ppr": [300.0, 250.0, 350.0],
    })

    result = stats_helpers.add_group_ranks(df, ["fp_ppr"], ["season", "position"])

    ranks = result["fp_ppr_rank"].tolist()
    assert ranks == [2, 3, 1]

def test_add_group_ranks_handles_ties() -> None:
    df = pd.DataFrame({
        "season": [2025, 2025],
        "position": ["WR", "WR"],
        "rec_yds": [1200.0, 1200.0],
    })

    result = stats_helpers.add_group_ranks(df, ["rec_yds"], ["season", "position"])

    assert result["rec_yds_rank"].tolist() == [1, 1]

def test_add_group_ranks_skips_missing_metrics() -> None:
    df = pd.DataFrame({"season": [2025], "position": ["QB"], "fp_ppr": [300.0]})

    result = stats_helpers.add_group_ranks(df, ["fp_ppr", "nonexistent"], ["season", "position"])

    assert "fp_ppr_rank" in result.columns
    assert "nonexistent_rank" not in result.columns
