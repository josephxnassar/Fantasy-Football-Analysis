"""FastAPI application setup, middleware, exception handlers, and router registration"""

import logging
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes.depth_chart_routes import router as depth_chart_router
from backend.api.routes.schedule_routes import router as schedule_router
from backend.api.routes.statistics_routes import router as statistics_router
from backend.api.routes.teams_routes import router as teams_router
from backend.app import App
from backend.config.settings import CORS_ALLOW_CREDENTIALS, CORS_ORIGINS
from backend.util.exceptions import CacheNotLoadedError, FantasyFootballError, PlayerNotFoundError

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Initialize cache-backed app state at startup and close resources on shutdown."""
    fantasy_app = App()
    fantasy_app.initialize(refresh_if_missing=False)
    app_instance.state.fantasy_app = fantasy_app
    try:
        yield
    finally:
        fantasy_app.db.close()

api = FastAPI(title="Fantasy Football API",
              description="API for dynasty and redraft player rankings",
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
    logger.warning(f"[{exc.source}] {exc}")
    return JSONResponse(status_code=503, content={"detail": str(exc)})

@api.exception_handler(PlayerNotFoundError)
async def player_not_found_handler(request: Request, exc: PlayerNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@api.exception_handler(FantasyFootballError)
async def fantasy_error_handler(request: Request, exc: FantasyFootballError) -> JSONResponse:
    logger.error(f"[{exc.source}] {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# ==================== ROUTES ====================

@api.get("/")
def read_root() -> Dict[str, str]:
    return {"status": "online",
            "message": "Fantasy Football Analysis API",
            "version": "0.1.0"}

api.include_router(statistics_router)
api.include_router(teams_router)
api.include_router(schedule_router)
api.include_router(depth_chart_router)
