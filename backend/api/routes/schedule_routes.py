"""Schedule API routes — team schedules"""
import math
from typing import Optional, SupportsInt

from fastapi import APIRouter, Request

from backend.api.models import TeamScheduleGame, TeamScheduleResponse
from backend.api.util.cache_helpers import get_app_caches, get_cache
from backend.api.util.team_helpers import get_team_schedule_entry, validate_team
from backend.util import constants

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


def _to_optional_int(value: object) -> Optional[int]:
    """Convert scalar schedule values into nullable ints."""
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if not value or value.upper() == "BYE":
            return None
        try:
            return int(value)
        except ValueError:
            return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, SupportsInt):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    return None


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
        team_score = _to_optional_int(row.get('team_score'))
        opponent_score = _to_optional_int(row.get('opponent_score'))
        winner: Optional[str] = None

        if opponent == 'BYE':
            bye_week = int(week)
            home_away = None
            team_score = None
            opponent_score = None
        elif team_score is not None and opponent_score is not None:
            if team_score > opponent_score:
                winner = team
            elif opponent_score > team_score:
                winner = opponent
            else:
                winner = "TIE"

        schedule.append(
            TeamScheduleGame(
                week=int(week),
                opponent=opponent,
                home_away=home_away,
                team_score=team_score,
                opponent_score=opponent_score,
                winner=winner,
            )
        )

    return TeamScheduleResponse(team=team,
                                team_name=constants.TEAM_NAMES.get(team, team),
                                season=target_season,
                                available_seasons=available_seasons,
                                schedule=schedule,
                                bye_week=bye_week)
