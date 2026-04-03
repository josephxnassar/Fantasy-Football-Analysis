"""Unit tests for Statistics._build_all_players."""

import pandas as pd
import pytest

from backend.statistics import statistics as statistics_module
from backend.statistics.statistics import Statistics

# normal

def test_build_all_players_returns_valid_player_payloads_and_meta(statistics: Statistics, monkeypatch: pytest.MonkeyPatch) -> None:
    """_build_all_players returns only valid players and the derived roster meta counts."""
    player_key = ("Jayden Daniels", "1")
    ignored_key = ("Ignored Player", "2")
    monkeypatch.setattr(statistics_module.stats_helpers, "build_all_players_lookups", lambda rosters, current_season: (
        {player_key: "QB", ignored_key: "RB"},
        {player_key: 24},
        {player_key},
        {player_key: "headshot"},
        {player_key: "WSH"},
        {player_key},
    ))

    all_players, roster_meta = statistics._build_all_players(pd.DataFrame(), {player_key})

    assert all_players == [{
        "name": "Jayden Daniels",
        "player_id": "1",
        "position": "QB",
        "age": 24,
        "headshot_url": "headshot",
        "team": "WSH",
        "is_rookie": True,
        "is_eligible": True,
    }]
    assert roster_meta == {
        "player_positions_count": 2,
        "player_ages_count": 1,
        "eligible_player_count": 1,
        "headshot_player_count": 1,
        "player_teams_count": 1,
        "rookie_player_count": 1,
    }

# edge

def test_build_all_players_returns_empty_payload_when_no_player_keys_are_valid(statistics: Statistics, monkeypatch: pytest.MonkeyPatch) -> None:
    """_build_all_players returns an empty player payload when no keys are valid."""
    player_key = ("Jayden Daniels", "1")
    monkeypatch.setattr(statistics_module.stats_helpers, "build_all_players_lookups", lambda rosters, current_season: (
        {player_key: "QB"},
        {},
        set(),
        {},
        {},
        set(),
    ))

    all_players, roster_meta = statistics._build_all_players(pd.DataFrame(), set())

    assert all_players == []
    assert roster_meta == {
        "player_positions_count": 1,
        "player_ages_count": 0,
        "eligible_player_count": 0,
        "headshot_player_count": 0,
        "player_teams_count": 0,
        "rookie_player_count": 0,
    }

# exception

def test_build_all_players_propagates_lookup_failure(statistics: Statistics, monkeypatch: pytest.MonkeyPatch) -> None:
    """_build_all_players propagates a lookup helper failure."""
    def raise_error(rosters: pd.DataFrame, current_season: int):
        raise RuntimeError("dummy")

    monkeypatch.setattr(statistics_module.stats_helpers, "build_all_players_lookups", raise_error)

    with pytest.raises(RuntimeError, match="dummy"):
        statistics._build_all_players(pd.DataFrame(), set())
