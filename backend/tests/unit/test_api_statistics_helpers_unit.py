from copy import deepcopy

import pytest
from fastapi import HTTPException

from backend.api.util.api_statistics_helpers import (
    build_consistency_chart_players,
    build_overall_chart_players,
    build_player_trend_points,
    build_position_chart_players,
    find_player_team,
    get_player_profile,
    resolve_chart_season,
)


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

def test_build_position_chart_players_includes_position_and_age(stats_cache) -> None:
    season_data = stats_cache["by_year"][2025]
    players_by_name = {player["name"]: player for player in stats_cache["all_players"]}

    players = build_position_chart_players(season_data["QB"], "QB", players_by_name)

    assert players[0]["name"] == "Patrick Mahomes"
    assert players[0]["position"] == "QB"
    assert players[0]["age"] == 30

def test_find_player_team_from_depth_charts(depth_chart_cache) -> None:
    team = find_player_team("Patrick Mahomes", depth_chart_cache)
    assert team == "KC"

def test_build_consistency_chart_players_uses_weekly_points(stats_cache) -> None:
    season_data = stats_cache["by_year"][2025]
    players_by_name = {player["name"]: player for player in stats_cache["all_players"]}
    weekly_by_player = deepcopy(stats_cache["player_weekly_stats"])
    weekly_by_player["Patrick Mahomes"] = [
        {"season": 2025, "week": 1, "fp_ppr": 24.8},
        {"season": 2025, "week": 2, "fp_ppr": 19.2},
    ]
    weekly_by_player["JaMarr Chase"] = [
        {"season": 2025, "week": 1, "fp_ppr": 21.4},
        {"season": 2025, "week": 2, "fp_ppr": 33.9},
    ]

    players = build_consistency_chart_players(
        season_data=season_data,
        weekly_by_player=weekly_by_player,
        players_by_name=players_by_name,
        position="Overall",
        season=2025,
        top_n=10,
    )

    names = {player["name"] for player in players}
    assert {"Patrick Mahomes", "JaMarr Chase"}.issubset(names)
    mahomes = next(player for player in players if player["name"] == "Patrick Mahomes")
    assert mahomes["games"] == 2
    assert mahomes["avg_fp_ppr"] == 22.0


def test_build_player_trend_points_returns_ordered_points(stats_cache) -> None:
    by_year = stats_cache["by_year"]

    available_seasons, points = build_player_trend_points(
        by_year=by_year,
        player_name="Patrick Mahomes",
        position="QB",
        stat="Pass Yds",
    )

    assert available_seasons == [2025, 2024]
    assert points == [
        {"season": 2024, "value": 4065.0},
        {"season": 2025, "value": 4280.0},
    ]


def test_build_player_trend_points_rejects_unknown_stat(stats_cache) -> None:
    by_year = stats_cache["by_year"]

    with pytest.raises(HTTPException) as exc_info:
        build_player_trend_points(
            by_year=by_year,
            player_name="Patrick Mahomes",
            position="QB",
            stat="not_a_stat",
        )

    assert exc_info.value.status_code == 400
    assert "Invalid stat" in exc_info.value.detail
