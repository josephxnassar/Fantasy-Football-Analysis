"""Teams API routes — shared team metadata"""

from fastapi import APIRouter

from backend.api.models import DivisionsResponse
from backend.util import constants

router = APIRouter(prefix="/api/teams", tags=["teams"])

_CONFERENCE_ORDER = ("AFC", "NFC")
_DIVISION_ORDER = ("North", "South", "East", "West")


@router.get("/divisions", response_model=DivisionsResponse)
def get_divisions() -> DivisionsResponse:
    """Get NFL division structure for team browsing across features."""
    team_names = {team: metadata["name"] for team, metadata in constants.TEAM_METADATA.items()}
    divisions = {
        conference: {
            division: [
                team
                for team, metadata in constants.TEAM_METADATA.items()
                if metadata["conference"] == conference and metadata["division"] == division
            ]
            for division in _DIVISION_ORDER
        }
        for conference in _CONFERENCE_ORDER
    }
    return DivisionsResponse(divisions=divisions,
                             team_names=team_names)
