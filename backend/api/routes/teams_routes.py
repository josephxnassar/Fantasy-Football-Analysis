"""Teams API routes — shared team metadata"""

from fastapi import APIRouter

from backend.api.models import DivisionsResponse
from backend.util import constants

router = APIRouter(prefix="/api/teams", tags=["teams"])

@router.get("/divisions", response_model=DivisionsResponse)
def get_divisions() -> DivisionsResponse:
    """Get NFL division structure for team browsing across features."""
    return DivisionsResponse(divisions=constants.NFL_DIVISIONS,
                             team_names=constants.TEAM_NAMES)
