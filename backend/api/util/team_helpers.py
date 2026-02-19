"""Team validation and schedule/depth-chart lookup helpers."""

from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException

from backend.api.util.cache_helpers import get_cache
from backend.util import constants

def get_team_cache(caches: Dict[str, Any], cache_name: str, team: str, label: str = "Data") -> Any:
    """Validate team, look up its entry in a cache, and return it."""
    team = validate_team(team)
    cache = get_cache(caches, cache_name)
    entry = cache.get(team)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"{label} not found for team '{team}'")
    return team, entry

def validate_team(team: str) -> str:
    """Validate and normalize a team abbreviation."""
    team = team.upper()
    if team not in constants.TEAMS:
        raise HTTPException(status_code=400,
                            detail=f"Invalid team. Must be one of: {', '.join(sorted(constants.TEAMS))}")
    return team

def get_team_schedule_entry(schedule_cache: Dict[Any, Dict[str, Any]], team: str, season: Optional[int]) -> Tuple[int, List[int], Any]:
    """Resolve a team schedule entry with season support for nested schedule cache."""
    available_seasons = get_available_schedule_seasons(schedule_cache, team)
    if not available_seasons:
        raise HTTPException(status_code=404, detail=f"Schedule not found for team '{team}'")
    if season is not None and season not in available_seasons:
        raise HTTPException(status_code=400,
                            detail=f"Invalid season for team '{team}'. Available: {', '.join(map(str, available_seasons))}")
    target_season = season or available_seasons[0]
    team_schedule_df = schedule_cache.get(target_season, {}).get(team)
    if team_schedule_df is None:
        raise HTTPException(status_code=404, detail=f"Schedule not found for team '{team}' in season {target_season}")
    return target_season, available_seasons, team_schedule_df

def get_available_schedule_seasons(schedule_cache: Dict[Any, Dict[str, Any]], team: str) -> List[int]:
    """Return available schedule seasons for a team from nested schedule cache."""
    return sorted([int(season) for season, teams in schedule_cache.items() if isinstance(teams, dict) and team in teams], reverse=True)
