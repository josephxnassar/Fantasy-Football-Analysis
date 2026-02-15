import pandas as pd
import pytest

from backend.statistics.util import stats_helpers

pytestmark = pytest.mark.unit


def test_add_derived_stats_handles_zero_division() -> None:
    df = pd.DataFrame(
        {
            "Rec Yds": [100.0, 0.0],
            "Rec": [5.0, 0.0],
            "Rush Yds": [80.0, 20.0],
            "Carries": [20.0, 0.0],
        }
    )

    result = stats_helpers.add_derived_stats(df)

    assert "Yds/Rec" in result.columns
    assert "Yds/Rush" in result.columns
    assert result.loc[0, "Yds/Rec"] == 20.0
    assert result.loc[1, "Yds/Rec"] == 0.0
    assert result.loc[0, "Yds/Rush"] == 4.0
    assert result.loc[1, "Yds/Rush"] == 0.0


def test_calculate_age_multiplier_behaviors() -> None:
    young_wr = stats_helpers.calculate_age_multiplier(age=22, position="WR")
    peak_wr = stats_helpers.calculate_age_multiplier(age=26, position="WR")
    old_rb = stats_helpers.calculate_age_multiplier(age=30, position="RB")

    assert young_wr > 1.0
    assert peak_wr == 1.0
    assert 0.1 <= old_rb < 1.0


def test_rank_calculations_exclude_ineligible_players() -> None:
    ratings = {"A": 100.0, "B": 90.0, "C": 80.0}
    positions = {"A": "QB", "B": "QB", "C": "RB"}
    eligible = {"A", "C"}

    overall = stats_helpers.calculate_overall_ranks(ratings, eligible)
    by_position = stats_helpers.calculate_position_ranks(ratings, positions, eligible)

    assert overall == {"A": 1, "C": 2}
    assert by_position == {"A": 1, "C": 1}


def test_build_all_players_includes_expected_fields() -> None:
    redraft = {"A": 100.0, "B": 85.0}
    dynasty = {"A": 96.0, "B": 90.0}
    positions = {"A": "QB", "B": "WR"}
    eligible = {"A"}
    ages = {"A": 28, "B": 24}
    headshots = {"A": "https://img/a.png"}
    teams = {"A": "KC", "B": "CIN"}
    rookies = {"B": True}
    overall_red = {"A": 1}
    overall_dyn = {"A": 1}
    pos_red = {"A": 1}
    pos_dyn = {"A": 1}

    players = stats_helpers.build_all_players(
        redraft,
        dynasty,
        positions,
        eligible,
        ages,
        headshots,
        teams,
        rookies,
        overall_red,
        overall_dyn,
        pos_red,
        pos_dyn,
    )

    by_name = {player["name"]: player for player in players}
    assert set(by_name) == {"A", "B"}
    assert by_name["A"]["is_eligible"] is True
    assert by_name["B"]["is_eligible"] is False
    assert by_name["B"]["is_rookie"] is True
    assert by_name["A"]["pos_rank_redraft"] == 1
