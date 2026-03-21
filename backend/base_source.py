"""Abstract base class for data sources."""

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class BaseSource(ABC):
    """Abstract base for all data sources (Statistics, Schedules, DepthChart)."""

    def __init__(self, seasons: list[int]) -> None:
        self.cache: Any = None
        self.seasons = seasons

    def get_cache(self) -> Any:
        """Return cached data."""
        return self.cache

    def set_cache(self, cache: Any) -> None:
        """Set cached data."""
        self.cache = cache

    @abstractmethod
    def run(self) -> None:
        """Process data and populate cache."""
        pass
