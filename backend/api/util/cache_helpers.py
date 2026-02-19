"""Cache access helpers for FastAPI routes."""

from typing import Any, Dict, cast

from fastapi import Request

from backend.util.exceptions import CacheNotLoadedError

def get_app_caches(request: Request) -> Dict[str, Any]:
    """Return in-memory caches attached to FastAPI app state."""
    fantasy_app = getattr(request.app.state, "fantasy_app", None)
    if fantasy_app is None or not hasattr(fantasy_app, "caches"):
        raise CacheNotLoadedError("Application cache not initialized", source="cache_helpers")
    return cast(Dict[str, Any], fantasy_app.caches)

def get_cache(caches: Dict[str, Any], name: str) -> Dict[str, Any]:
    """Get cache by name, raising CacheNotLoadedError if not loaded."""
    cache = caches.get(name, {})
    if not isinstance(cache, dict) or not cache:
        raise CacheNotLoadedError(f"{name} data not loaded", source="cache_helpers")
    return cast(Dict[str, Any], cache)
