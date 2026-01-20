from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Dict, Optional
import logging
import pandas as pd

from backend.app import App
from backend.models import (
    RankingsResponse, PlayerResponse, SearchResponse
)
from backend.util import constants
from backend.util.position_multipliers import calculate_age_multiplier, calculate_redraft_multiplier, get_default_age
from backend.util.api_helpers import (
    find_player_in_cache,
    get_player_available_seasons,
    find_player_team,
    filter_stats,
    calculate_enriched_rankings
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
api = FastAPI(
    title="Fantasy Football API",
    description="API for dynasty and redraft player rankings",
    version="0.1.0"
)

# Add CORS middleware for frontend communication
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the data app
app = App()
app.load()  # Load cached data


@api.get("/")
def read_root() -> Dict[str, str]:
    """Root endpoint - API status"""
    return {
        "status": "online",
        "message": "Fantasy Football Analysis API",
        "version": "0.1.0"
    }


@api.get("/api/rankings", response_model=RankingsResponse)
def get_rankings(
    format: str = "redraft",
    position: Optional[str] = None
) -> RankingsResponse:
    """Get player rankings with both redraft and dynasty ratings/percentiles
    
    - **format**: redraft or dynasty (for backward compatibility, unused in computation)
    - **position**: QB, RB, WR, TE (optional)
    """
    # Validate inputs
    if format not in constants.VALID_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid format. Must be one of: {', '.join(constants.VALID_FORMATS)}"
        )
    if position and position not in constants.POSITIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid position. Must be one of: {', '.join(constants.POSITIONS)}"
        )
    
    try:
        # Get statistics from cache
        stats_cache = app.caches.get("Statistics", {})
        if not stats_cache:
            raise HTTPException(status_code=503, detail="Statistics data not loaded")
        
        # Use shared function to calculate enriched rankings
        all_players = calculate_enriched_rankings(stats_cache, position)
        
        # Group by position for response
        computed_by_position = {}
        for player in all_players:
            pos = player['position']
            if pos not in computed_by_position:
                computed_by_position[pos] = []
            computed_by_position[pos].append(player)
        
        # Determine which positions to return
        positions_to_fetch = [position] if position else constants.POSITIONS
        rankings_by_position = {
            pos: computed_by_position.get(pos, [])
            for pos in positions_to_fetch
            if pos in computed_by_position
        }
        
        return RankingsResponse(
            format=format,
            position=position,
            model="ridge",
            rankings=rankings_by_position
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching rankings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch rankings")


@api.get("/api/player/{player_name}", response_model=PlayerResponse)
def get_player(player_name: str, season: Optional[int] = None) -> PlayerResponse:
    """
    Get detailed player information including stats and team
    
    - **player_name**: The player's name (e.g., "Ja'Marr Chase")
    - **season**: Optional season year (e.g., 2024). If not provided, returns averaged stats with rating.
    """
    try:
        stats_cache = app.caches.get("Statistics", {})
        
        # Determine which data source to use and get player data
        if season is not None:
            by_year_stats = stats_cache.get('by_year', {})
            season_stats = by_year_stats.get(season, {})
            
            if not season_stats:
                raise HTTPException(status_code=404, detail=f"No data available for season {season}")
            
            player_data, player_position = find_player_in_cache(player_name, season_stats)
        else:
            averaged_stats = stats_cache.get('averaged', stats_cache)
            player_data, player_position = find_player_in_cache(player_name, averaged_stats)
        
        if not player_data:
            raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
        
        # Apply redraft multiplier to rating if showing averaged data
        if season is None and 'Rating' in player_data:
            redraft_mult = calculate_redraft_multiplier(player_position)
            player_data = dict(player_data)  # Convert to dict if needed
            player_data['Rating'] = player_data['Rating'] * redraft_mult
        
        # Get available seasons for this player (only if showing averaged data)
        player_seasons = []
        if season is None:
            by_year_stats = stats_cache.get('by_year', {})
            player_seasons = get_player_available_seasons(player_name, by_year_stats)
        
        # Filter and format stats
        filtered_stats = filter_stats(player_data, constants.INTEGER_STATS)
        
        # Get player's team from depth charts
        depth_charts = app.caches.get("ESPNDepthChart", {})
        player_team = find_player_team(player_name, depth_charts)
        
        return PlayerResponse(
            name=player_name,
            position=player_position,
            team=player_team,
            stats=filtered_stats,
            available_seasons=player_seasons
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching player {player_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch player details")


@api.get("/api/search")
def search_players(q: str, position: Optional[str] = None) -> SearchResponse:
    """
    Search for players by name
    
    - **q**: Search query (player name or partial name)
    - **position**: Filter by position (QB, RB, WR, TE) (optional)
    """
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    try:
        stats_cache = app.caches.get("Statistics", {})
        if not stats_cache:
            raise HTTPException(status_code=503, detail="Statistics data not loaded")
        
        # Use shared function to calculate enriched rankings
        all_players = calculate_enriched_rankings(stats_cache, position)
        
        # Filter to search query
        query_lower = q.lower()
        results = [
            {
                "name": player['name'],
                "position": player['position'],
                "rating": player['Rating'],
                "Rating": player['Rating'],
                "DynastyRating": player['DynastyRating'],
                "pos_percentile_redraft": player['pos_percentile_redraft'],
                "pos_percentile_dynasty": player['pos_percentile_dynasty'],
                "overall_percentile_redraft": player['overall_percentile_redraft'],
                "overall_percentile_dynasty": player['overall_percentile_dynasty']
            }
            for player in all_players
            if query_lower in player['name'].lower()
        ]
        
        # Sort by rating descending
        results.sort(key=lambda x: x["rating"], reverse=True)
        
        return SearchResponse(
            query=q,
            results=results[:20],  # Limit to 20 results
            count=len(results)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching for players: {e}")
        raise HTTPException(status_code=500, detail="Failed to search players")
