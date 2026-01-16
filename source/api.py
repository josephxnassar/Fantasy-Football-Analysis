from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from source.app import App
from source.models import RankingsResponse, PlayerResponse, ScheduleResponse, ErrorResponse
import logging
import json
import os

logger = logging.getLogger(__name__)

# Initialize FastAPI app
api = FastAPI(
    title="Fantasy Football API",
    description="API for dynasty and redraft player rankings with schedule analysis",
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

# Load defense tiers
defense_tiers_path = os.path.join(os.path.dirname(__file__), "data", "defense_tiers.json")
defense_tiers = {}
if os.path.exists(defense_tiers_path):
    with open(defense_tiers_path, 'r') as f:
        defense_tiers = json.load(f)


def get_matchup_quality(position: str, opponent: str, week: int = 1, season: int = 2025) -> str:
    """
    Get matchup quality rating for a position vs opponent
    
    Returns: 'elite', 'good', 'neutral', 'bad', 'worst', or None if not found
    """
    try:
        season_tiers = defense_tiers.get(str(season), {})
        week_key = f"week_{week}"
        week_tiers = season_tiers.get(week_key, {})
        position_tiers = week_tiers.get(position, {})
        
        for quality, opponents in position_tiers.items():
            if opponent in opponents:
                return quality.replace("_matchups", "")
        return "neutral"
    except Exception as e:
        logger.warning(f"Error getting matchup quality for {position} vs {opponent}: {e}")
        return None


@api.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with proper response format"""
    return {"error": exc.detail}


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
    position: str = None,      # QB, RB, WR, TE or None for all
    model: str = "ridge"       # linear, ridge, or lasso
):
    """
    Get player rankings filtered by format, position, and model
    
    - **format**: redraft or dynasty
    - **position**: QB, RB, WR, TE (optional)
    - **model**: linear, ridge, or lasso
    """
    # Validate inputs
    valid_formats = ["redraft", "dynasty"]
    valid_positions = ["QB", "RB", "WR", "TE"]
    valid_models = ["linear", "ridge", "lasso"]
    
    if format not in valid_formats:
        raise HTTPException(status_code=400, detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}")
    if model not in valid_models:
        raise HTTPException(status_code=400, detail=f"Invalid model. Must be one of: {', '.join(valid_models)}")
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
                df = stats_cache[pos]
                # Convert DataFrame to list of dicts
                player_rankings = df.reset_index().to_dict("records")
                rankings_by_position[pos] = player_rankings
        
        return RankingsResponse(
            format=format,
            position=position,
            model=model,
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
    Get detailed player information including stats and upcoming schedule
    
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
        
        # Get player's schedule if they have a team (from depth charts)
        depth_charts = app.caches.get("ESPNDepthChart", {})
        player_team = None
        
        # Try to find team from depth charts
        for team, dc_data in depth_charts.items():
            if isinstance(dc_data, dict) and player_name in str(dc_data):
                player_team = team
                break
        
        # Get upcoming schedule for the team
        schedule_data = []
        if player_team:
            schedules = app.caches.get("Schedules", {})
            if player_team in schedules:
                team_schedule = schedules[player_team]
                # Convert schedule to list format with matchup quality
                raw_schedule = team_schedule.reset_index().to_dict("records") if hasattr(team_schedule, 'reset_index') else []
                for game in raw_schedule:
                    matchup_quality = get_matchup_quality(player_position, game.get('Opponent'), game.get('week', 1))
                    schedule_data.append({
                        'week': game.get('week'),
                        'opponent': game.get('Opponent'),
                        'matchup_quality': matchup_quality
                    })
        
        return PlayerResponse(
            name=player_name,
            position=player_position,
            team=player_team,
            stats=player_data,
            schedule=schedule_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching player {player_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch player details")


@api.get("/api/schedule/{team}", response_model=ScheduleResponse)
def get_schedule(team: str):
    """
    Get team schedule with bye weeks and opponents
    
    - **team**: Team abbreviation (e.g., KC, SF, LAR, WSH)
    """
    # Validate team
    valid_teams = ["KC", "SF", "DAL", "PHI", "NYE", "GB", "MIN", "DET", "TB", "NO", "ATL", "CAR",
                   "NYG", "WAS", "LAR", "SEA", "ARI", "CHI", "BAL", "PIT", "CLE", "BUF", "MIA",
                   "NE", "IND", "HOU", "TEN", "JAX", "LAC", "LV", "DEN"]
    
    team_upper = team.upper()
    if team_upper not in valid_teams:
        raise HTTPException(status_code=400, detail=f"Invalid team abbreviation: {team}. Must be a valid NFL team.")
    
    try:
        # Get team schedule from cache
        schedules = app.caches.get("Schedules", {})
        
        if team_upper not in schedules:
            raise HTTPException(status_code=404, detail=f"Schedule not found for team {team_upper}")
        
        team_schedule = schedules[team_upper]
        
        # Convert to list of dicts
        schedule_list = team_schedule.reset_index().to_dict("records") if hasattr(team_schedule, 'reset_index') else []
        
        return ScheduleResponse(
            team=team_upper,
            schedule=schedule_list
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching schedule for {team}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch schedule")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)
