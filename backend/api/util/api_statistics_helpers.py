"""Statistics cache transformation and lookup helpers."""

from typing import Any, Dict, List, Optional, Tuple, cast

import pandas as pd
from fastapi import HTTPException

from backend.util import constants


def get_player_profile(stats_cache: Dict[str, Any], player_name: str, season: Optional[int] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str], List[int], Optional[Dict[str, Any]]]:
    """Get player season stats, position, available seasons, and metadata row from cache."""
    player_meta = next((player for player in get_all_players(stats_cache) if player.get("name") == player_name), None)
    by_year_stats = stats_cache.get(constants.STATS["BY_YEAR"], {})

    stats_dict: Optional[Dict[str, Any]] = None
    position: Optional[str] = None
    available_seasons: List[int] = []

    for year in sorted(by_year_stats.keys(), reverse=True):
        season_frames = by_year_stats.get(year, {})
        for pos, df in season_frames.items():
            if not isinstance(df, pd.DataFrame) or player_name not in df.index:
                continue
            available_seasons.append(year)
            if (season is None and stats_dict is None) or season == year:
                stats_dict = df.loc[player_name].to_dict()
                position = pos
            break

    return stats_dict, position, available_seasons, player_meta

def find_player_team(player_name: str, depth_charts: Dict[str, Any]) -> Optional[str]:
    """Find a player's current team from depth chart values."""
    for team, df in depth_charts.items():
        if isinstance(df, pd.DataFrame) and player_name in df.values:
            return team
    return None

def get_all_players(stats_cache: Dict[str, Any], position_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return all cached players, optionally filtered by position."""
    players = cast(List[Dict[str, Any]], stats_cache.get(constants.STATS["ALL_PLAYERS"], []))
    if position_filter:
        return [player for player in players if player.get("position") == position_filter]
    return players

def resolve_chart_season(by_year: Dict[int, Dict[str, pd.DataFrame]], season: Optional[int]) -> Tuple[int, List[int], Dict[str, pd.DataFrame]]:
    """Resolve chart season and return available seasons and selected season data."""
    available = sorted(by_year.keys(), reverse=True)
    if not available:
        raise HTTPException(status_code=404, detail="No seasonal data available")
    if season is not None and season not in available:
        raise HTTPException(status_code=400,
                            detail=f"Invalid season. Available: {', '.join(map(str, available))}")
    target_season = season if season is not None else available[0]
    return target_season, available, by_year.get(target_season, {})

def build_position_chart_players(df: pd.DataFrame, players_by_name: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build chart rows for a single position DataFrame."""
    players: List[Dict[str, Any]] = []
    numeric_stats = df.select_dtypes(include="number").to_dict(orient="index")
    for player_name, stats in numeric_stats.items():
        player_meta = players_by_name.get(player_name, {})
        players.append({"name": player_name,
                        "team": player_meta.get("team"),
                        "headshot_url": player_meta.get("headshot_url"),
                        "stats": stats})
    return players

def build_overall_chart_players(season_data: Dict[str, pd.DataFrame], players_by_name: Dict[str, Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Build chart rows across all positions in a season."""
    players: List[Dict[str, Any]] = []
    stat_columns = set()
    for position, df in season_data.items():
        if df is None or df.empty:
            continue
        numeric_stats = df.select_dtypes(include="number").to_dict(orient="index")
        for player_name, stats in numeric_stats.items():
            player_meta = players_by_name.get(player_name, {})
            stat_columns.update(stats.keys())
            players.append({"name": player_name,
                            "position": position,
                            "team": player_meta.get("team"),
                            "headshot_url": player_meta.get("headshot_url"),
                            "stats": stats})
    return players, sorted(stat_columns)
