"""Cache access helpers for FastAPI routes."""

from typing import Any, Dict

from fastapi import Request

from backend.util.exceptions import CacheNotLoadedError

def get_app_caches(request: Request) -> Dict[str, Any]:
    """Return in-memory caches attached to FastAPI app state."""
    fantasy_app = getattr(request.app.state, "fantasy_app", None)
    if fantasy_app is None or not hasattr(fantasy_app, "caches"):
        raise CacheNotLoadedError("Application cache not initialized", source="cache_helpers")
    return fantasy_app.caches

def get_cache(caches: Dict[str, Any], name: str) -> Dict:
    """Get cache by name, raising CacheNotLoadedError if not loaded."""
    cache = caches.get(name, {})
    if not cache:
        raise CacheNotLoadedError(f"{name} data not loaded", source="cache_helpers")
    return cache
