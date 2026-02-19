"""Statistics API routes — rankings, player details, search, and chart data"""

import heapq
from typing import Optional

from fastapi import APIRouter, HTTPException, Request

from backend.api.models import (ChartDataResponse, ChartPlayerEntry, PlayerResponse, PlayerSearchResult, RankingsResponse, SearchResponse)
from backend.api.util.api_statistics_helpers import (get_ranked_players,
                                                     get_all_players,
                                                     get_player_profile,
                                                     group_rankings_by_position,
                                                     find_player_team,
                                                     resolve_chart_season,
                                                     build_position_chart_players,
                                                     build_overall_chart_players)
from backend.api.util.cache_helpers import get_app_caches, get_cache
from backend.api.util.search_helpers import filter_search_results
from backend.util import constants
from backend.util.exceptions import PlayerNotFoundError

router = APIRouter(prefix="/api", tags=["statistics"])
_VALID_CHART_POSITIONS = constants.POSITIONS + ["Overall"]

@router.get("/rankings", response_model=RankingsResponse)
def get_rankings(request: Request, format: str = "redraft", position: Optional[str] = None) -> RankingsResponse:
    """Get player rankings by format with optional position filter"""
    if format not in constants.VALID_FORMATS:
        raise HTTPException(status_code=400,
                            detail=f"Invalid format. Must be one of: {', '.join(constants.VALID_FORMATS)}")
    if position and position not in constants.POSITIONS:
        raise HTTPException(status_code=400,
                            detail=f"Invalid position. Must be one of: {', '.join(constants.POSITIONS)}")

    caches = get_app_caches(request)
    stats_cache = get_cache(caches, constants.CACHE["STATISTICS"])
    all_players = get_ranked_players(stats_cache, position)
    rankings_by_position = group_rankings_by_position(all_players, format_name=format)

    return RankingsResponse(format=format,
                            position=position,
                            model="ridge",
                            rankings=rankings_by_position)

@router.get("/player/{player_name}", response_model=PlayerResponse)
def get_player(request: Request, player_name: str, season: Optional[int] = None) -> PlayerResponse:
    """Get detailed stats for a specific player"""
    caches = get_app_caches(request)
    stats_cache = get_cache(caches, constants.CACHE["STATISTICS"])
    stats_dict, position, available_seasons, player_meta = get_player_profile(stats_cache, player_name, season)
    if not stats_dict or not position:
        raise PlayerNotFoundError(f"Player '{player_name}' not found", source="api")

    depth_charts = caches.get(constants.CACHE["DEPTH_CHART"], {})

    return PlayerResponse(name=player_name,
                          position=position,
                          team=(player_meta or {}).get("team") or find_player_team(player_name, depth_charts),
                          stats=stats_dict,
                          available_seasons=available_seasons,
                          headshot_url=(player_meta or {}).get("headshot_url"),
                          weekly_stats=stats_cache.get(constants.STATS["PLAYER_WEEKLY_STATS"], {}).get(player_name),
                          ranking_data=player_meta)

@router.get("/search", response_model=SearchResponse)
def search_players(request: Request, q: str, position: Optional[str] = None) -> SearchResponse:
    """Search for players by name"""
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")

    caches = get_app_caches(request)
    stats_cache = get_cache(caches, constants.CACHE["STATISTICS"])
    all_players = get_all_players(stats_cache, position)

    results = filter_search_results(all_players, q)
    top_results = heapq.nlargest(20, results, key=lambda x: x.get("redraft_rating", 0))
    typed_results = [PlayerSearchResult(**result) for result in top_results]

    return SearchResponse(query=q,
                          results=typed_results,
                          count=len(results))

@router.get("/chart-data", response_model=ChartDataResponse)
def get_chart_data(request: Request, position: str, season: Optional[int] = None) -> ChartDataResponse:
    """Get player stat data for chart visualisation."""
    if position not in _VALID_CHART_POSITIONS:
        raise HTTPException(status_code=400,
                            detail=f"Invalid position. Must be one of: {', '.join(_VALID_CHART_POSITIONS)}")

    caches = get_app_caches(request)
    stats_cache = get_cache(caches, constants.CACHE["STATISTICS"])
    by_year = stats_cache.get(constants.STATS["BY_YEAR"], {})
    player_meta_by_name = {player["name"]: player for player in get_all_players(stats_cache) if player.get("name")}
    target_season, available, season_data = resolve_chart_season(by_year, season)

    if position == "Overall":
        players, stat_columns = build_overall_chart_players(season_data, player_meta_by_name)
        typed_players = [ChartPlayerEntry(**player) for player in players]
        return ChartDataResponse(season=target_season,
                                 position=position,
                                 available_seasons=available,
                                 stat_columns=stat_columns,
                                 players=typed_players)

    df = season_data.get(position)
    if df is None or df.empty:
        return ChartDataResponse(season=target_season,
                                 position=position,
                                 available_seasons=available,
                                 stat_columns=[],
                                 players=[])

    players = build_position_chart_players(df, player_meta_by_name)
    stat_columns = sorted(df.select_dtypes(include="number").columns.tolist())
    typed_players = [ChartPlayerEntry(**player) for player in players]

    return ChartDataResponse(season=target_season,
                             position=position,
                             available_seasons=available,
                             stat_columns=stat_columns,
                             players=typed_players)
