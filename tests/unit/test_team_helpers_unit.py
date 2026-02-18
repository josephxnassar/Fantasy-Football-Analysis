import pytest
from fastapi import HTTPException

from backend.api.util.team_helpers import (
    get_team_cache,
    get_team_schedule_entry,
    validate_team,
)
from backend.util import constants

pytestmark = pytest.mark.unit

def test_validate_team_normalizes_case() -> None:
    assert validate_team("kc") == "KC"

def test_validate_team_rejects_unknown_team() -> None:
    with pytest.raises(HTTPException) as exc_info:
        validate_team("XYZ")

    assert exc_info.value.status_code == 400
    assert "Invalid team" in exc_info.value.detail

def test_get_team_schedule_entry_returns_requested_season(schedules_cache) -> None:
    season, available, schedule_df = get_team_schedule_entry(schedules_cache, "KC", season=2025)

    assert season == 2025
    assert available == [2025, 2024]
    assert schedule_df.loc[2, "Opponent"] == "BYE"

def test_get_team_cache_raises_when_team_data_missing(depth_chart_cache) -> None:
    caches = {constants.CACHE["DEPTH_CHART"]: depth_chart_cache}
    with pytest.raises(HTTPException) as exc_info:
        get_team_cache(caches, constants.CACHE["DEPTH_CHART"], "ARI", label="Depth chart")

    assert exc_info.value.status_code == 404
    assert "Depth chart not found" in exc_info.value.detail
