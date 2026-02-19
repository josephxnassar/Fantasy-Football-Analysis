"""Schedule API routes — team schedules"""
from typing import Optional

from fastapi import APIRouter, Request

from backend.api.models import TeamScheduleResponse, TeamScheduleGame
from backend.api.util.cache_helpers import get_app_caches, get_cache
from backend.api.util.team_helpers import get_team_schedule_entry, validate_team
from backend.util import constants

router = APIRouter(prefix="/api/schedules", tags=["schedules"])

@router.get("/{team}", response_model=TeamScheduleResponse)
def get_team_schedule(request: Request, team: str, season: Optional[int] = None) -> TeamScheduleResponse:
    """Get schedule for a specific team"""
    caches = get_app_caches(request)
    team = validate_team(team)
    schedule_cache = get_cache(caches, constants.CACHE["SCHEDULES"])
    target_season, available_seasons, team_schedule_df = get_team_schedule_entry(schedule_cache, team, season)

    schedule = []
    bye_week = None

    for week, row in team_schedule_df.iterrows():
        opponent = row.get('opponent', 'BYE')
        home_away = row.get('home_away')
        if opponent == 'BYE':
            bye_week = int(week)
            home_away = None
        schedule.append(TeamScheduleGame(week=int(week), opponent=opponent, home_away=home_away))

    return TeamScheduleResponse(team=team,
                                team_name=constants.TEAM_NAMES.get(team, team),
                                season=target_season,
                                available_seasons=available_seasons,
                                schedule=schedule,
                                bye_week=bye_week)
