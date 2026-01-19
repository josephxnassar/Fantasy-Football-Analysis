from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.app import App
from backend.models import (
    RankingsResponse, PlayerResponse, SearchResponse
)
import logging

logger = logging.getLogger(__name__)

# Stats that should be displayed as whole numbers (counts, yards, TDs)
INTEGER_STATS = {
    'Comp', 'Att', 'Pass Yds', 'Pass TD', 'INT', 'Sacks', 'Sack Yds', 
    'Sack Fum', 'Sack Fum Lost', 'Air Yds', 'YAC', 'Pass 1st', 'Pass 2PT',
    'Carries', 'Rush Yds', 'Rush TD', 'Rush Fum', 'Rush Fum Lost', 'Rush 1st', 'Rush 2PT',
    'Rec', 'Tgt', 'Rec Yds', 'Rec TD', 'Rec Fum', 'Rec Fum Lost', 
    'Rec Air Yds', 'Rec YAC', 'Rec 1st', 'Rec 2PT', 'ST TD',
    'Fantasy Pts', 'PPR Pts'
}

# Age multiplier configuration for dynasty format by position
AGE_MULTIPLIERS = {
    'QB': {'peak_age': 28, 'young_boost': 1.3, 'decline_per_year': 0.05},
    'RB': {'peak_age': 24, 'young_boost': 1.5, 'decline_per_year': 0.15},     # Steepest decline
    'WR': {'peak_age': 26, 'young_boost': 1.4, 'decline_per_year': 0.08},
    'TE': {'peak_age': 27, 'young_boost': 1.3, 'decline_per_year': 0.07},
}

def calculate_age_multiplier(age: int, position: str) -> float:
    """
    Calculate age-based multiplier for dynasty format.
    Young players get a boost for upside, older players penalized heavily.
    """
    if position not in AGE_MULTIPLIERS:
        return 1.0
    
    config = AGE_MULTIPLIERS[position]
    peak_age = config['peak_age']
    young_boost = config['young_boost']
    decline_rate = config['decline_per_year']
    
    # Young players (under peak): boost for upside potential
    if age < peak_age:
        if age < 21:
            return young_boost * 0.9  # Very young, unproven
        # Scale from 1.0 at peak down to lower at age 21
        years_from_peak = peak_age - age
        # Linear from peak (1.0) to young_boost at age 21
        boost_factor = 1.0 + ((young_boost - 1.0) * years_from_peak / (peak_age - 21))
        return min(young_boost, boost_factor)
    
    # At peak age
    elif age == peak_age:
        return 1.0
    
    # Past peak: steep decline
    else:
        years_past_peak = age - peak_age
        multiplier = 1.0 - (years_past_peak * decline_rate)
        return max(0.1, multiplier)  # Floor at 10% to avoid going negative

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


def _find_player_in_cache(player_name: str, cache_data: dict) -> tuple:
    """Helper to find player and return (data, position). Returns (None, None) if not found."""
    for position, df in cache_data.items():
        if player_name in df.index:
            return df.loc[player_name].to_dict(), position
    return None, None


def _get_player_available_seasons(player_name: str, by_year_stats: dict) -> list:
    """Get list of seasons where player has data."""
    seasons = []
    for season, season_data in by_year_stats.items():
        for position, df in season_data.items():
            if player_name in df.index:
                seasons.append(season)
                break
    return seasons


@api.get("/")
def read_root():
    """Root endpoint - API status"""
    return {
        "status": "online",
        "message": "Fantasy Football Analysis API",
        "version": "0.1.0"
    }


@api.get("/api/rankings", response_model=RankingsResponse)
def get_rankings(
    format: str = "redraft",  # redraft or dynasty
    position: str = None       # QB, RB, WR, TE or None for all
):
    """
    Get player rankings filtered by format and position
    
    - **format**: redraft or dynasty
      - Redraft: Current season performance prioritized
      - Dynasty: Factors in longevity, age, upside (requires enhanced data)
    - **position**: QB, RB, WR, TE (optional)
    """
    # Validate inputs
    valid_formats = ["redraft", "dynasty"]
    valid_positions = ["QB", "RB", "WR", "TE"]
    
    if format not in valid_formats:
        raise HTTPException(status_code=400, detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}")
    if position and position not in valid_positions:
        raise HTTPException(status_code=400, detail=f"Invalid position. Must be one of: {', '.join(valid_positions)}")
    
    try:
        # Get statistics from cache
        stats_cache = app.caches.get("Statistics", {})
        if not stats_cache:
            raise HTTPException(status_code=503, detail="Statistics data not loaded")
        
        # Get averaged stats (with ratings) from new cache structure
        averaged_stats = stats_cache.get('averaged', stats_cache)  # Fallback to old structure
        eligible_players = set(stats_cache.get('eligible_players', []))
        player_ages = stats_cache.get('player_ages', {})  # Get ages for dynasty calculations
        
        # Build rankings response
        rankings_by_position = {}
        
        # Determine which positions to include
        positions_to_fetch = [position] if position else valid_positions
        
        for pos in positions_to_fetch:
            if pos in averaged_stats:
                df = averaged_stats[pos].copy()  # Make a copy to avoid modifying cached data

                # Filter to eligible (active) players for both formats
                if eligible_players:
                    df = df[df.index.isin(eligible_players)]
                
                # Dynasty: apply age multipliers to ratings
                if format == "dynasty" and 'Rating' in df.columns:
                    for player_name in df.index:
                        age = player_ages.get(player_name, 26)  # Default age 26 if not found
                        multiplier = calculate_age_multiplier(age, pos)
                        df.loc[player_name, 'Rating'] = df.loc[player_name, 'Rating'] * multiplier
                    
                    # Re-sort by updated ratings
                    df = df.sort_values(by='Rating', ascending=False)
                
                # Calculate percentile for each player
                rating_col = 'Rating' if 'Rating' in df.columns else df.columns[0]
                df['percentile'] = df[rating_col].rank(pct=True) * 100
                
                # Convert DataFrame to list of dicts
                player_rankings = df.reset_index().to_dict("records")
                
                rankings_by_position[pos] = player_rankings
        
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
def get_player(player_name: str, season: int = None):
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
            
            player_data, player_position = _find_player_in_cache(player_name, season_stats)
        else:
            averaged_stats = stats_cache.get('averaged', stats_cache)
            player_data, player_position = _find_player_in_cache(player_name, averaged_stats)
        
        if not player_data:
            raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
        
        # Get available seasons for this player (only if showing averaged data)
        player_seasons = []
        if season is None:
            by_year_stats = stats_cache.get('by_year', {})
            player_seasons = _get_player_available_seasons(player_name, by_year_stats)
        
        # Filter out stats with 0 or near-0 values (keep only meaningful stats)
        filtered_stats = {
            stat: value for stat, value in player_data.items() 
            if not (isinstance(value, (int, float)) and abs(value) < 0.01)
        }
        
        # Convert appropriate stats to whole numbers
        for stat in filtered_stats:
            if stat in INTEGER_STATS and isinstance(filtered_stats[stat], (int, float)):
                filtered_stats[stat] = int(round(filtered_stats[stat]))
        
        # Get player's team from depth charts
        depth_charts = app.caches.get("ESPNDepthChart", {})
        player_team = None
        
        for team, dc_data in depth_charts.items():
            try:
                for col in dc_data.columns:
                    if player_name in dc_data[col].values:
                        player_team = team
                        break
                if player_team:
                    break
            except Exception as e:
                logger.warning(f"Error searching depth chart for team {team}: {e}")
                continue
        
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
def search_players(q: str, position: str = None):
    """
    Search for players by name
    
    - **q**: Search query (player name or partial name)
    - **position**: Filter by position (QB, RB, WR, TE) (optional)
    """
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    try:
        stats_cache = app.caches.get("Statistics", {})
        averaged_stats = stats_cache.get('averaged', stats_cache)
        query_lower = q.lower()
        results = []
        
        for pos, df in averaged_stats.items():
            if position and pos != position:
                continue
            
            for player_name, row in df.iterrows():
                if query_lower in player_name.lower():
                    results.append({
                        "name": player_name,
                        "position": pos,
                        "rating": row["Rating"] if "Rating" in df.columns else 0
                    })
        
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)
