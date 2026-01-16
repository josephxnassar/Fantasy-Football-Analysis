from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from source.app import App
import logging

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


@api.get("/")
def read_root():
    """Root endpoint - API status"""
    return {
        "status": "online",
        "message": "Fantasy Football Analysis API",
        "version": "0.1.0"
    }


@api.get("/api/rankings")
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
    try:
        # Validate inputs
        valid_formats = ["redraft", "dynasty"]
        valid_positions = ["QB", "RB", "WR", "TE"]
        valid_models = ["linear", "ridge", "lasso"]
        
        if format not in valid_formats:
            return {"error": f"format must be one of {valid_formats}"}, 400
        if model not in valid_models:
            return {"error": f"model must be one of {valid_models}"}, 400
        if position and position not in valid_positions:
            return {"error": f"position must be one of {valid_positions}"}, 400
        
        # Get statistics from cache
        stats_cache = app.caches.get("Statistics", {})
        if not stats_cache:
            return {"error": "Statistics data not loaded"}, 500
        
        # Build rankings response
        rankings_by_position = {}
        
        # Determine which positions to include
        positions_to_fetch = [position] if position else valid_positions
        
        for pos in positions_to_fetch:
            if pos in stats_cache:
                df = stats_cache[pos]
                # Convert DataFrame to list of dicts, sorted by rating (descending)
                # Assuming the dataframe is already sorted by rating from the model
                player_rankings = df.reset_index().to_dict("records")
                rankings_by_position[pos] = player_rankings
        
        return {
            "format": format,
            "position": position,
            "model": model,
            "rankings": rankings_by_position
        }
    except Exception as e:
        logger.error(f"Error fetching rankings: {e}")
        return {"error": str(e)}, 500


@api.get("/api/player/{player_name}")
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
            return {"error": f"Player '{player_name}' not found"}, 404
        
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
                # Convert schedule to list format
                schedule_data = team_schedule.reset_index().to_dict("records") if hasattr(team_schedule, 'reset_index') else []
        
        return {
            "name": player_name,
            "position": player_position,
            "team": player_team,
            "stats": player_data,
            "schedule": schedule_data
        }
    except Exception as e:
        logger.error(f"Error fetching player {player_name}: {e}")
        return {"error": str(e)}, 500


@api.get("/api/schedule/{team}")
def get_schedule(team: str):
    """
    Get team schedule with bye weeks and opponents
    
    - **team**: Team abbreviation (e.g., KC, SF, LAR, WSH)
    """
    try:
        # Validate team
        valid_teams = ["KC", "SF", "DAL", "PHI", "NYE", "GB", "MIN", "DET", "TB", "NO", "ATL", "CAR",
                       "NYG", "WAS", "LAR", "SEA", "ARI", "CHI", "BAL", "PIT", "CLE", "BUF", "MIA",
                       "NE", "IND", "HOU", "TEN", "JAX", "LAC", "LV", "DEN"]
        
        team_upper = team.upper()
        if team_upper not in valid_teams:
            return {"error": f"Invalid team: {team}. Must be valid NFL team abbreviation."}, 400
        
        # Get team schedule from cache
        schedules = app.caches.get("Schedules", {})
        
        if team_upper not in schedules:
            return {"error": f"Schedule not found for team {team_upper}"}, 404
        
        team_schedule = schedules[team_upper]
        
        # Convert to list of dicts
        schedule_list = team_schedule.reset_index().to_dict("records") if hasattr(team_schedule, 'reset_index') else []
        
        return {
            "team": team_upper,
            "schedule": schedule_list
        }
    except Exception as e:
        logger.error(f"Error fetching schedule for {team}: {e}")
        return {"error": str(e)}, 500


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)
