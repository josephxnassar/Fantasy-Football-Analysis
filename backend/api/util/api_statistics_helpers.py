"""Statistics cache transformation and lookup helpers."""

from statistics import mean, pstdev
from typing import Any, Dict, List, Mapping, Optional, Tuple, cast

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

def build_position_chart_players(df: pd.DataFrame, position: str, players_by_name: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build chart rows for a single position DataFrame."""
    players: List[Dict[str, Any]] = []
    numeric_stats = df.select_dtypes(include="number").to_dict(orient="index")
    for player_name, stats in numeric_stats.items():
        player_meta = players_by_name.get(player_name, {})
        players.append({"name": player_name,
                        "position": position,
                        "age": player_meta.get("age"),
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
                            "age": player_meta.get("age"),
                            "team": player_meta.get("team"),
                            "headshot_url": player_meta.get("headshot_url"),
                            "stats": stats})
    return players, sorted(stat_columns)

def _to_float(value: Any) -> Optional[float]:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return None
    return float(numeric)

def _resolve_fp_value(stats: Mapping[str, Any]) -> Optional[float]:
    for key in ("fp_ppr", "fantasy_points_ppr", "fantasy_points", "fp_std", "PPR Pts", "Non-PPR Pts"):
        if key in stats:
            resolved = _to_float(stats.get(key))
            if resolved is not None:
                return resolved
    return None

def _season_weekly_points(weekly_records: List[Dict[str, Any]], season: int) -> List[float]:
    points: List[float] = []
    for week in weekly_records:
        week_season = _to_float(week.get("season"))
        if week_season is None or int(week_season) != season:
            continue
        fp_value = _resolve_fp_value(week)
        if fp_value is None:
            continue
        points.append(fp_value)
    return points

def build_consistency_chart_players(season_data: Dict[str, pd.DataFrame], weekly_by_player: Dict[str, List[Dict[str, Any]]], players_by_name: Dict[str, Dict[str, Any]], position: str, season: int, top_n: int) -> List[Dict[str, Any]]:
    """Build weekly consistency/upside chart rows from seasonal and weekly caches."""
    seasonal_candidates: List[Tuple[str, str, float]] = []
    position_frames = season_data.items() if position == "Overall" else [(position, season_data.get(position))]

    for pos_label, df in position_frames:
        if not isinstance(df, pd.DataFrame) or df.empty:
            continue
        numeric_stats = df.select_dtypes(include="number").to_dict(orient="index")
        for player_name, stats in numeric_stats.items():
            seasonal_fp = _resolve_fp_value(stats)
            if seasonal_fp is None:
                continue
            seasonal_candidates.append((player_name, pos_label, seasonal_fp))

    sorted_candidates = sorted(seasonal_candidates, key=lambda row: row[2], reverse=True)[:top_n]
    chart_rows: List[Dict[str, Any]] = []

    for player_name, pos_label, _ in sorted_candidates:
        weekly_records = weekly_by_player.get(player_name, [])
        weekly_points = _season_weekly_points(weekly_records, season)
        if not weekly_points:
            continue
        player_meta = players_by_name.get(player_name, {})
        chart_rows.append({"name": player_name,
                           "position": pos_label,
                           "age": player_meta.get("age"),
                           "team": player_meta.get("team"),
                           "headshot_url": player_meta.get("headshot_url"),
                           "games": len(weekly_points),
                           "avg_fp_ppr": round(mean(weekly_points), 2),
                           "ceiling_fp_ppr": round(max(weekly_points), 2),
                           "volatility_fp_ppr": round(pstdev(weekly_points), 2)})

    return chart_rows
