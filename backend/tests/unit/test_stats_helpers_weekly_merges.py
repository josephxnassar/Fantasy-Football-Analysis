import pandas as pd
import pytest

from backend.statistics.statistics import Statistics
from backend.statistics.util import stats_helpers


@pytest.fixture
def statistics_source() -> Statistics:
    return Statistics([2025])


def test_merge_weekly_statistics_data_aligns_pfr_names_before_merge(statistics_source: Statistics) -> None:
    sources = {
        "player_weekly": pd.DataFrame(
            {
                "season": [2025],
                "week": [1],
                "game_id": ["2025_01_NE_BUF"],
                "player_display_name": ["Joe Milton III"],
                "position": ["QB"],
                "team": ["NE"],
            }
        ),
        "snap_counts": pd.DataFrame(),
        "ff_opp_weekly": pd.DataFrame(),
        "nextgen_pass_weekly": pd.DataFrame(),
        "nextgen_rec_weekly": pd.DataFrame(),
        "nextgen_rush_weekly": pd.DataFrame(),
        "pfr_pass_weekly": pd.DataFrame(
            {
                "season": [2025],
                "week": [1],
                "game_id": ["2025_01_NE_BUF"],
                "player_display_name": ["Joe Milton"],
                "team": ["NE"],
                "pfr_pass_bad_throws": [2.0],
            }
        ),
        "pfr_rush_weekly": pd.DataFrame(columns=["season", "week", "game_id", "player_display_name", "team"]),
        "pfr_rec_weekly": pd.DataFrame(columns=["season", "week", "game_id", "player_display_name", "team"]),
    }

    merged = statistics_source._merge_weekly_statistics_data(sources)

    assert merged.loc[0, "pfr_pass_bad_throws"] == 2.0


def test_merge_weekly_statistics_data_merges_ff_opp_when_base_game_id_is_null(statistics_source: Statistics) -> None:
    sources = {
        "player_weekly": pd.DataFrame(
            {
                "season": [2024],
                "week": [1],
                "game_id": [pd.NA],
                "player_id": ["00-0031234"],
                "player_display_name": ["DJ Moore"],
                "position": ["WR"],
                "team": ["CHI"],
            }
        ),
        "snap_counts": pd.DataFrame(),
        "ff_opp_weekly": pd.DataFrame(
            {
                "season": [2024],
                "week": [1],
                "game_id": ["2024_01_CHI_TEN"],
                "player_id": ["00-0031234"],
                "player_display_name": ["DJ Moore"],
                "position": ["WR"],
                "team": ["CHI"],
                "ffo_total_fp_exp": [18.25],
            }
        ),
        "nextgen_pass_weekly": pd.DataFrame(),
        "nextgen_rec_weekly": pd.DataFrame(),
        "nextgen_rush_weekly": pd.DataFrame(),
        "pfr_pass_weekly": pd.DataFrame(),
        "pfr_rush_weekly": pd.DataFrame(),
        "pfr_rec_weekly": pd.DataFrame(),
    }

    merged = statistics_source._merge_weekly_statistics_data(sources)

    assert merged.loc[0, "ffo_total_fp_exp"] == pytest.approx(18.25)


def test_merge_weekly_statistics_data_merges_ff_opp_when_name_differs_but_player_id_matches(statistics_source: Statistics) -> None:
    sources = {
        "player_weekly": pd.DataFrame(
            {
                "season": [2022],
                "week": [4],
                "game_id": ["2022_04_SEA_DET"],
                "player_id": ["00-0038134"],
                "player_display_name": ["Kenneth Walker III"],
                "position": ["RB"],
                "team": ["SEA"],
            }
        ),
        "snap_counts": pd.DataFrame(),
        "ff_opp_weekly": pd.DataFrame(
            {
                "season": [2022],
                "week": [4],
                "game_id": ["2022_04_SEA_DET"],
                "player_id": ["00-0038134"],
                "player_display_name": ["Kenneth Walker"],
                "position": ["RB"],
                "team": ["SEA"],
                "ffo_total_fp_exp": [14.7],
            }
        ),
        "nextgen_pass_weekly": pd.DataFrame(),
        "nextgen_rec_weekly": pd.DataFrame(),
        "nextgen_rush_weekly": pd.DataFrame(),
        "pfr_pass_weekly": pd.DataFrame(),
        "pfr_rush_weekly": pd.DataFrame(),
        "pfr_rec_weekly": pd.DataFrame(),
    }

    merged = statistics_source._merge_weekly_statistics_data(sources)

    assert merged.loc[0, "player_display_name"] == "Kenneth Walker III"
    assert "player_display_name_x" not in merged.columns
    assert "player_display_name_y" not in merged.columns
    assert merged.loc[0, "ffo_total_fp_exp"] == pytest.approx(14.7)


def test_merge_weekly_statistics_data_merges_ff_opp_when_name_differs_by_punctuation_but_player_id_matches(statistics_source: Statistics) -> None:
    sources = {
        "player_weekly": pd.DataFrame(
            {
                "season": [2022],
                "week": [8],
                "game_id": ["2022_08_CAR_ATL"],
                "player_id": ["00-0034827"],
                "player_display_name": ["DJ Moore"],
                "position": ["WR"],
                "team": ["CAR"],
            }
        ),
        "snap_counts": pd.DataFrame(),
        "ff_opp_weekly": pd.DataFrame(
            {
                "season": [2022],
                "week": [8],
                "game_id": ["2022_08_CAR_ATL"],
                "player_id": ["00-0034827"],
                "player_display_name": ["D.J. Moore"],
                "position": ["WR"],
                "team": ["CAR"],
                "ffo_total_fp_exp": [17.4],
            }
        ),
        "nextgen_pass_weekly": pd.DataFrame(),
        "nextgen_rec_weekly": pd.DataFrame(),
        "nextgen_rush_weekly": pd.DataFrame(),
        "pfr_pass_weekly": pd.DataFrame(),
        "pfr_rush_weekly": pd.DataFrame(),
        "pfr_rec_weekly": pd.DataFrame(),
    }

    merged = statistics_source._merge_weekly_statistics_data(sources)

    assert merged.loc[0, "player_display_name"] == "DJ Moore"
    assert "player_display_name_x" not in merged.columns
    assert "player_display_name_y" not in merged.columns
    assert merged.loc[0, "ffo_total_fp_exp"] == pytest.approx(17.4)


def test_merge_weekly_statistics_data_merges_snap_counts_when_base_game_id_is_null_and_name_differs(statistics_source: Statistics) -> None:
    sources = {
        "player_weekly": pd.DataFrame(
            {
                "season": [2024],
                "week": [1],
                "game_id": [pd.NA],
                "player_id": ["00-0031234"],
                "player_display_name": ["Joe Milton III"],
                "position": ["QB"],
                "team": ["NE"],
            }
        ),
        "snap_counts": pd.DataFrame(
            {
                "season": [2024],
                "week": [1],
                "game_id": ["2024_01_NE_CIN"],
                "player_display_name": ["Joe Milton"],
                "position": ["QB"],
                "team": ["NE"],
                "sc_offense_pct": [0.82],
            }
        ),
        "ff_opp_weekly": pd.DataFrame(),
        "nextgen_pass_weekly": pd.DataFrame(),
        "nextgen_rec_weekly": pd.DataFrame(),
        "nextgen_rush_weekly": pd.DataFrame(),
        "pfr_pass_weekly": pd.DataFrame(),
        "pfr_rush_weekly": pd.DataFrame(),
        "pfr_rec_weekly": pd.DataFrame(),
    }

    merged = statistics_source._merge_weekly_statistics_data(sources)

    assert merged.loc[0, "sc_offense_pct"] == pytest.approx(0.82)


def test_merge_weekly_statistics_data_merges_nextgen_receiving_when_name_differs(statistics_source: Statistics) -> None:
    sources = {
        "player_weekly": pd.DataFrame(
            {
                "season": [2023],
                "week": [1],
                "game_id": ["2023_01_GB_CHI"],
                "player_display_name": ["DJ Moore"],
                "position": ["WR"],
                "team": ["CHI"],
            }
        ),
        "snap_counts": pd.DataFrame(),
        "ff_opp_weekly": pd.DataFrame(),
        "nextgen_pass_weekly": pd.DataFrame(),
        "nextgen_rec_weekly": pd.DataFrame(
            {
                "season": [2023],
                "week": [1],
                "player_display_name": ["D.J. Moore"],
                "position": ["WR"],
                "team": ["CHI"],
                "ng_rec_avg_separation": [3.4],
                "ng_rec_catch_pct": [72.0],
            }
        ),
        "nextgen_rush_weekly": pd.DataFrame(),
        "pfr_pass_weekly": pd.DataFrame(),
        "pfr_rush_weekly": pd.DataFrame(),
        "pfr_rec_weekly": pd.DataFrame(),
    }

    merged = statistics_source._merge_weekly_statistics_data(sources)

    assert merged.loc[0, "ng_rec_avg_separation"] == pytest.approx(3.4)
    assert merged.loc[0, "ng_rec_catch_pct"] == pytest.approx(72.0)


def test_merge_weekly_statistics_data_merges_nextgen_rushing_when_name_differs(statistics_source: Statistics) -> None:
    sources = {
        "player_weekly": pd.DataFrame(
            {
                "season": [2023],
                "week": [1],
                "game_id": ["2023_01_LA_SEA"],
                "player_display_name": ["Kenneth Walker III"],
                "position": ["RB"],
                "team": ["SEA"],
            }
        ),
        "snap_counts": pd.DataFrame(),
        "ff_opp_weekly": pd.DataFrame(),
        "nextgen_pass_weekly": pd.DataFrame(),
        "nextgen_rec_weekly": pd.DataFrame(),
        "nextgen_rush_weekly": pd.DataFrame(
            {
                "season": [2023],
                "week": [1],
                "player_display_name": ["Kenneth Walker"],
                "position": ["RB"],
                "team": ["SEA"],
                "ng_rush_efficiency": [4.8],
                "ng_rush_rush_yds_over_exp_per_att": [0.7],
            }
        ),
        "pfr_pass_weekly": pd.DataFrame(),
        "pfr_rush_weekly": pd.DataFrame(),
        "pfr_rec_weekly": pd.DataFrame(),
    }

    merged = statistics_source._merge_weekly_statistics_data(sources)

    assert merged.loc[0, "ng_rush_efficiency"] == pytest.approx(4.8)
    assert merged.loc[0, "ng_rush_rush_yds_over_exp_per_att"] == pytest.approx(0.7)


def test_merge_seasonal_statistics_data_merges_pfr_rush_tot_row_without_team_match(statistics_source: Statistics) -> None:
    sources = {
        "player_seasonal": pd.DataFrame(
            {
                "season": [2022],
                "player_display_name": ["Christian McCaffrey"],
                "team": ["SF"],
                "position": ["RB"],
            }
        ),
        "pfr_pass_season": pd.DataFrame(),
        "pfr_rush_season": pd.DataFrame(
            {
                "season": [2022],
                "player_display_name": ["Christian McCaffrey"],
                "team": ["2TM"],
                "position": ["RB"],
                "pfr_rush_yac": [456.0],
                "pfr_rush_yac_att": [1.9],
                "pfr_rush_ybc_att": [2.8],
                "pfr_rush_brk_tkl": [10.0],
            }
        ),
        "pfr_rec_season": pd.DataFrame(),
    }

    merged = statistics_source._merge_seasonal_statistics_data(sources)

    assert merged.loc[0, "team"] == "SF"
    assert merged.loc[0, "pfr_rush_yac"] == pytest.approx(456.0)
    assert merged.loc[0, "pfr_rush_yac_att"] == pytest.approx(1.9)
    assert merged.loc[0, "pfr_rush_ybc_att"] == pytest.approx(2.8)
    assert merged.loc[0, "pfr_rush_brk_tkl"] == pytest.approx(10.0)


def test_merge_seasonal_statistics_data_merges_pfr_rec_tot_row_without_team_match(statistics_source: Statistics) -> None:
    sources = {
        "player_seasonal": pd.DataFrame(
            {
                "season": [2022],
                "player_display_name": ["Christian McCaffrey"],
                "team": ["SF"],
                "position": ["RB"],
            }
        ),
        "pfr_pass_season": pd.DataFrame(),
        "pfr_rush_season": pd.DataFrame(),
        "pfr_rec_season": pd.DataFrame(
            {
                "season": [2022],
                "player_display_name": ["Christian McCaffrey"],
                "team": ["2TM"],
                "position": ["RB"],
                "pfr_rec_yac": [695.0],
                "pfr_rec_yac_r": [8.2],
                "pfr_rec_brk_tkl": [8.0],
            }
        ),
    }

    merged = statistics_source._merge_seasonal_statistics_data(sources)

    assert merged.loc[0, "team"] == "SF"
    assert merged.loc[0, "pfr_rec_yac"] == pytest.approx(695.0)
    assert merged.loc[0, "pfr_rec_yac_r"] == pytest.approx(8.2)
    assert merged.loc[0, "pfr_rec_brk_tkl"] == pytest.approx(8.0)


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


def test_align_pfr_seasonal_names_handles_missing_name_column() -> None:
    base_df = pd.DataFrame({"player_display_name": ["Patrick Mahomes"]})
    pfr_df = pd.DataFrame({"stat": [5]})

    aligned = stats_helpers.align_pfr_seasonal_names(pfr_df, base_df)

    assert aligned.equals(pfr_df)
