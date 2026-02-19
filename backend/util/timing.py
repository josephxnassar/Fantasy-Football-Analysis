"""Minimal timing helper."""

from __future__ import annotations

import functools
import logging
from time import perf_counter
from typing import Any, Callable, TypeVar, cast

from backend.config.settings import TIMING_ENABLED

F = TypeVar("F", bound=Callable[..., Any])

class Timer:
    """Simple context manager for elapsed-time logging."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.logger = logging.getLogger("backend.timing")
        self._start = 0.0

    def __enter__(self) -> "Timer":
        if not TIMING_ENABLED:
            return self
        self._start = perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if not TIMING_ENABLED:
            return
        elapsed = perf_counter() - self._start
        status = "failed" if exc_type is not None else "completed"
        self.logger.info("timer=%s | status=%s | elapsed=%.3fs", self.name, status, elapsed)

def timed(name: str | None = None) -> Callable[[F], F]:
    """Decorator for timing a function with `Timer`."""
    def decorator(func: F) -> F:
        timer_name = name or func.__qualname__
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with Timer(timer_name):
                return func(*args, **kwargs)
        return cast(F, wrapper)
    return decorator
