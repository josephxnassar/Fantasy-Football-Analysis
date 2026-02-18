"""Depth chart API routes — team depth charts"""

import pandas as pd
from fastapi import APIRouter, Request

from backend.api.models import DepthChartEntry, TeamDepthChartResponse
from backend.api.util.cache_helpers import get_app_caches
from backend.api.util.team_helpers import get_team_cache
from backend.util import constants

router = APIRouter(prefix="/api/depth-charts", tags=["depth_charts"])

def _normalize_depth_value(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    return text or None

@router.get("/{team}", response_model=TeamDepthChartResponse)
def get_team_depth_chart(request: Request, team: str) -> TeamDepthChartResponse:
    """Get depth chart for a specific team"""
    caches = get_app_caches(request)
    team, df = get_team_cache(caches, constants.CACHE["DEPTH_CHART"], team, label="Depth chart")

    return TeamDepthChartResponse(team=team,
                                  team_name=constants.TEAM_NAMES.get(team, team),
                                  depth_chart= [DepthChartEntry(position=position,
                                                                starter=_normalize_depth_value(row.get('Starter')),
                                                                second=_normalize_depth_value(row.get('2nd')),
                                                                third=_normalize_depth_value(row.get('3rd')),
                                                                fourth=_normalize_depth_value(row.get('4th'))) for position, row in df.iterrows()])
