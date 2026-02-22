import pytest
from fastapi import HTTPException

from backend.api.util.api_statistics_helpers import (
    build_overall_chart_players,
    find_player_team,
    get_player_profile,
    resolve_chart_season,
)

pytestmark = pytest.mark.unit

def test_get_player_profile_uses_most_recent_season(stats_cache) -> None:
    stats, position, seasons, player_meta = get_player_profile(stats_cache, "Patrick Mahomes")

    assert position == "QB"
    assert seasons == [2025, 2024]
    assert player_meta["name"] == "Patrick Mahomes"
    assert stats["Pass TD"] == 32

def test_resolve_chart_season_rejects_invalid_year(stats_cache) -> None:
    by_year = stats_cache["by_year"]
    with pytest.raises(HTTPException) as exc_info:
        resolve_chart_season(by_year, season=1999)

    assert exc_info.value.status_code == 400
    assert "Invalid season" in exc_info.value.detail

def test_build_overall_chart_players_aggregates_across_positions(stats_cache) -> None:
    season_data = stats_cache["by_year"][2025]
    players_by_name = {player["name"]: player for player in stats_cache["all_players"]}

    players, stat_columns = build_overall_chart_players(season_data, players_by_name)
    names = {player["name"] for player in players}
    positions = {player["position"] for player in players}

    assert {"Patrick Mahomes", "JaMarr Chase"}.issubset(names)
    assert {"QB", "WR"}.issubset(positions)
    assert "Pass Yds" in stat_columns
    assert "Rec Yds" in stat_columns

def test_find_player_team_from_depth_charts(depth_chart_cache) -> None:
    team = find_player_team("Patrick Mahomes", depth_chart_cache)
    assert team == "KC"
