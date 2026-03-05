"""FastAPI application setup, middleware, exception handlers, and router registration"""

import logging
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.models import AppInfoResponse
from backend.api.routes.depth_chart_routes import router as depth_chart_router
from backend.api.routes.schedule_routes import router as schedule_router
from backend.api.routes.statistics_routes import router as statistics_router
from backend.api.routes.teams_routes import router as teams_router
from backend.api.util.cache_helpers import get_app_caches, get_cache
from backend.app import App
from backend.config.settings import CORS_ALLOW_CREDENTIALS, CORS_ORIGINS
from backend.util import constants
from backend.util.exceptions import CacheNotLoadedError, FantasyFootballError, PlayerNotFoundError

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Initialize cache-backed app state at startup and close resources on shutdown."""
    fantasy_app = App()
    fantasy_app.initialize()
    app_instance.state.fantasy_app = fantasy_app
    try:
        yield
    finally:
        fantasy_app.db.close()

api = FastAPI(title="Fantasy Football API",
              description="API for player statistics, schedules, depth charts, and charts",
              version="0.1.0",
              lifespan=lifespan)

allow_credentials = CORS_ALLOW_CREDENTIALS and CORS_ORIGINS != ["*"]
if CORS_ALLOW_CREDENTIALS and CORS_ORIGINS == ["*"]:
    logger.warning(
        "CORS_ALLOW_CREDENTIALS=true ignored because CORS_ORIGINS is '*'. "
        "Set explicit origins to allow credentialed browser requests."
    )

api.add_middleware(CORSMiddleware,
                   allow_origins=CORS_ORIGINS,
                   allow_credentials=allow_credentials,
                   allow_methods=["*"],
                   allow_headers=["*"])

# ==================== EXCEPTION HANDLERS ====================

@api.exception_handler(CacheNotLoadedError)
async def cache_not_loaded_handler(request: Request, exc: CacheNotLoadedError) -> JSONResponse:
    logger.warning("[%s] %s", exc.source, exc)
    return JSONResponse(status_code=503, content={"detail": str(exc)})

@api.exception_handler(PlayerNotFoundError)
async def player_not_found_handler(request: Request, exc: PlayerNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@api.exception_handler(FantasyFootballError)
async def fantasy_error_handler(request: Request, exc: FantasyFootballError) -> JSONResponse:
    logger.error("[%s] %s", exc.source, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# ==================== ROUTES ====================

@api.get("/")
def read_root() -> Dict[str, str]:
    return {"status": "online",
            "message": "Fantasy Football Analysis API",
            "version": "0.1.0"}


@api.get("/api/app-info", response_model=AppInfoResponse)
def get_app_info(request: Request) -> AppInfoResponse:
    """Return application overview metadata for the landing page."""
    caches = get_app_caches(request)
    stats_cache = get_cache(caches, constants.CACHE["STATISTICS"])
    all_players = stats_cache.get(constants.STATS["ALL_PLAYERS"], [])
    by_year = stats_cache.get(constants.STATS["BY_YEAR"], {})
    weekly_stats = stats_cache.get(constants.STATS["PLAYER_WEEKLY_STATS"], {})

    # Players active in the current season
    current_season_positions = by_year.get(constants.CURRENT_SEASON, {})
    current_season_players = sum(len(df) for df in current_season_positions.values())

    # Total weekly game logs across all players/seasons
    total_game_logs = sum(len(weeks) for weeks in weekly_stats.values())

    # Count rookies and stat columns
    rookie_count = sum(1 for p in all_players if p.get("is_rookie"))
    stat_columns = 0
    for season_map in by_year.values():
        if not isinstance(season_map, dict):
            continue
        for df in season_map.values():
            if hasattr(df, "columns"):
                stat_columns = max(stat_columns, len(df.columns))

    return AppInfoResponse(
        seasons=constants.SEASONS,
        current_season=constants.CURRENT_SEASON,
        total_players=len(all_players),
        current_season_players=current_season_players,
        total_game_logs=total_game_logs,
        rookie_count=rookie_count,
        stat_columns=stat_columns,
    )


api.include_router(statistics_router)
api.include_router(teams_router)
api.include_router(schedule_router)
api.include_router(depth_chart_router)
