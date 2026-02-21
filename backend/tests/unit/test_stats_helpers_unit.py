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
