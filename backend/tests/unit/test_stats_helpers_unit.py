import pandas as pd
import pytest

from backend.statistics.util import stats_helpers

pytestmark = pytest.mark.unit

def test_add_derived_stats_handles_zero_division() -> None:
    df = pd.DataFrame({"Rec Yds": [100.0, 0.0],
                       "Rec": [5.0, 0.0],
                       "Rush Yds": [80.0, 20.0],
                       "Carries": [20.0, 0.0]})

    result = stats_helpers.add_derived_stats(df)

    assert "Yds/Rec" in result.columns
    assert "Yds/Rush" in result.columns
    assert result.loc[0, "Yds/Rec"] == 20.0
    assert result.loc[1, "Yds/Rec"] == 0.0
    assert result.loc[0, "Yds/Rush"] == 4.0
    assert result.loc[1, "Yds/Rush"] == 0.0

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
