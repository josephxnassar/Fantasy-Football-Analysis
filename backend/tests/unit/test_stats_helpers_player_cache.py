import pandas as pd
import pytest

from backend.statistics.statistics import RosterData, Statistics
from backend.util.exceptions import DataLoadError


class _NflReadPyResult:
    """Simple nflreadpy-like wrapper exposing to_pandas()."""

    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df

    def to_pandas(self) -> pd.DataFrame:
        return self._df


@pytest.fixture
def statistics_source() -> Statistics:
    return Statistics([2025])


def test_load_nextgen_receiving_stats_normalizes_team_abbreviations(monkeypatch: pytest.MonkeyPatch, statistics_source: Statistics) -> None:
    source_df = pd.DataFrame(
        {
            "season": [2025],
            "week": [1],
            "player_display_name": ["Puka Nacua"],
            "player_position": ["WR"],
            "team_abbr": ["LA"],
            "avg_separation": [2.8],
        }
    )

    monkeypatch.setattr(
        "backend.statistics.loaders.nfl.load_nextgen_stats",
        lambda **_: _NflReadPyResult(source_df),
    )

    loaded = statistics_source._source_loader.load_nextgen_receiving_stats()

    assert loaded.iloc[0]["team"] == "LAR"


def test_load_pfr_adv_rec_season_normalizes_team_abbreviations(monkeypatch: pytest.MonkeyPatch, statistics_source: Statistics) -> None:
    source_df = pd.DataFrame(
        {
            "season": [2025],
            "player": ["Puka Nacua"],
            "tm": ["LA"],
            "pos": ["WR"],
            "adot": [9.3],
        }
    )

    monkeypatch.setattr(
        "backend.statistics.loaders.nfl.load_pfr_advstats",
        lambda **_: _NflReadPyResult(source_df),
    )

    loaded = statistics_source._source_loader.load_pfr_adv_rec_season()

    assert loaded.iloc[0]["team"] == "LAR"


def test_load_player_weekly_stats_requires_structural_columns(monkeypatch: pytest.MonkeyPatch, statistics_source: Statistics) -> None:
    source_df = pd.DataFrame(
        {
            "season": [2025],
            "week": [1],
            "game_id": ["2025_01_LAR_DET"],
            "player_id": ["00-0037834"],
            "player_display_name": ["Puka Nacua"],
            "position": ["WR"],
            "season_type": ["REG"],
        }
    )

    monkeypatch.setattr(
        "backend.statistics.loaders.nfl.load_player_stats",
        lambda **_: _NflReadPyResult(source_df),
    )

    with pytest.raises(DataLoadError, match="player_weekly missing required columns: team"):
        statistics_source._source_loader.load_player_weekly_stats()


def test_build_all_players_includes_expected_fields(statistics_source: Statistics) -> None:
    positions = {"A": "QB", "B": "WR"}
    eligible = {"A"}
    ages = {"A": 28, "B": 24}
    headshots = {"A": "https://img/a.png"}
    teams = {"A": "KC", "B": "CIN"}
    rookies = {"B": True}

    players = statistics_source._build_all_players(
        RosterData(
            positions=positions,
            ages=ages,
            eligible=eligible,
            headshots=headshots,
            teams=teams,
            rookies=rookies,
        )
    )

    by_name = {player["name"]: player for player in players}
    assert set(by_name) == {"A", "B"}
    assert by_name["A"]["is_eligible"] is True
    assert by_name["B"]["is_eligible"] is False
    assert by_name["B"]["is_rookie"] is True
    assert by_name["A"]["team"] == "KC"


def test_collect_stats_player_names_and_filter_all_players(statistics_source: Statistics) -> None:
    seasonal_df = pd.DataFrame(
        {
            "season": [2024],
            "position": ["RB"],
            "player_display_name": ["Kenneth Walker III"],
            "rush_yds": [100.0],
        }
    )
    weekly_df = pd.DataFrame(
        {
            "season": [2024],
            "week": [1],
            "position": ["RB"],
            "player_display_name": ["Kenneth Walker III"],
            "rush_yds": [64.0],
        }
    )

    names = statistics_source._collect_stats_player_names(seasonal_df, weekly_df)
    assert names == {"Kenneth Walker III"}

    players = statistics_source._build_all_players(
        RosterData(
            positions={"Kenneth Walker": "RB", "Kenneth Walker III": "RB"},
            ages={"Kenneth Walker": 23, "Kenneth Walker III": 24},
            eligible={"Kenneth Walker", "Kenneth Walker III"},
            headshots={},
            teams={},
            rookies={},
        ),
        valid_player_names=names,
    )
    assert [player["name"] for player in players] == ["Kenneth Walker III"]


def test_build_seasonal_player_stats_replaces_nan_values_for_json_safety(statistics_source: Statistics) -> None:
    seasonal_df = pd.DataFrame(
        {
            "season": [2025],
            "position": ["WR"],
            "player_display_name": ["Test Receiver"],
            "team": [pd.NA],
            "receiving_epa": [float("nan")],
            "receiving_yards": [120.0],
        }
    )

    seasonal_data = statistics_source._build_seasonal_player_stats(seasonal_df)
    row = seasonal_data[2025]["WR"].loc["Test Receiver"]
    assert row["receiving_epa"] == 0.0
    assert row["team"] is None


def test_build_weekly_player_stats_replaces_nan_values_for_json_safety(statistics_source: Statistics) -> None:
    weekly_df = pd.DataFrame(
        {
            "season": [2025],
            "week": [1],
            "player_display_name": ["Test Receiver"],
            "receiving_epa": [float("nan")],
            "target_share": [0.2],
        }
    )

    weekly = statistics_source._build_weekly_player_stats(weekly_df)
    record = weekly["Test Receiver"][0]
    assert record["receiving_epa"] is None
    assert record["target_share"] == 0.2
