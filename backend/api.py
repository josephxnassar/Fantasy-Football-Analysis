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
        
        # Build rankings response
        rankings_by_position = {}
        
        # Determine which positions to include
        positions_to_fetch = [position] if position else valid_positions
        
        for pos in positions_to_fetch:
            if pos in stats_cache:
                df = stats_cache[pos].copy()  # Make a copy to avoid modifying cached data
                
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
def get_player(player_name: str):
    """
    Get detailed player information including stats and team
    
    - **player_name**: The player's name (e.g., "Ja'Marr Chase")
    """
    try:
        # Search for player in Statistics cache
        stats_cache = app.caches.get("Statistics", {})
        player_data = None
        player_position = None
        
        # Find player across all positions
        for position, df in stats_cache.items():
            if player_name in df.index:
                player_data = df.loc[player_name].to_dict()
                player_position = position
                break
        
        if not player_data:
            raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
        
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
        
        # Search through each team's depth chart
        for team, dc_data in depth_charts.items():
            try:
                # Check if player name appears in any column of this team's depth chart
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
            stats=filtered_stats
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
        query_lower = q.lower()
        results = []
        
        for pos, df in stats_cache.items():
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
