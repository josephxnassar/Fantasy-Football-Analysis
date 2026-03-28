"""FastAPI application setup."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app import App
from backend.config.logging_config import setup_logging
from backend.config.settings import get_api_refresh
from backend.util.exceptions import CacheNotLoadedError, FantasyFootballError, PlayerNotFoundError

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(api: FastAPI):
    """Load backend caches on startup and close resources on shutdown."""
    setup_logging()
    backend_app = App()
    api.state.backend_app = backend_app
    try:
        backend_app.run(refresh=get_api_refresh())
        yield
    finally:
        backend_app.close()

def create_app() -> FastAPI:
    """Create the API application."""
    return FastAPI(
        title="Fantasy Football Analysis API",
        version="0.2.0",
        lifespan=lifespan,
    )

app = create_app()

@app.exception_handler(CacheNotLoadedError)
async def cache_not_loaded_handler(request: Request, exc: CacheNotLoadedError) -> JSONResponse:
    """Return a cache-not-loaded response."""
    logger.warning("[%s] %s", exc.source, exc)
    return JSONResponse(status_code=503, content={"detail": str(exc)})

@app.exception_handler(PlayerNotFoundError)
async def player_not_found_handler(request: Request, exc: PlayerNotFoundError) -> JSONResponse:
    """Return a player-not-found response."""
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(FantasyFootballError)
async def fantasy_error_handler(request: Request, exc: FantasyFootballError) -> JSONResponse:
    """Return a generic fantasy-football error response."""
    logger.error("[%s] %s", exc.source, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.get("/")
def read_root() -> dict[str, str]:
    """Return basic API information."""
    return {
        "name": "Fantasy Football Analysis API",
        "version": "0.2.0",
        "health": "/health",
        "docs": "/docs",
    }

@app.get("/health")
def health(request: Request) -> dict[str, object]:
    """Return a minimal API health response."""
    backend_app = request.app.state.backend_app
    return {"ok": True, "cache_count": len(backend_app.caches)}
