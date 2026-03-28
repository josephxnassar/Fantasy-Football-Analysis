"""FastAPI application setup."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app import App
from backend.config.logging_config import setup_logging
from backend.config.settings import get_api_refresh

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
