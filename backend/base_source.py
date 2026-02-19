"""Abstract base class for data sources"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import pandas as pd

from backend.util import constants

logger = logging.getLogger(__name__)

class BaseSource(ABC):
    """Abstract base for all data sources (Statistics, Schedules, DepthChart)"""
    
    def __init__(self, seasons: List[int]) -> None:
        self.cache: Dict[Any, Any] = {}
        self.seasons: List[int] = seasons

    def get_keys(self) -> List[str]:
        """Return cache keys for this source"""
        return constants.TEAMS

    def get_cache(self) -> Dict[Any, Any]:
        """Return cached data"""
        return self.cache

    def set_cache(self, cache: Dict[Any, Any]) -> None:
        """Set cached data"""
        self.cache = cache

    @abstractmethod
    def _load(self) -> pd.DataFrame:
        """Load raw data from source"""
        pass

    @abstractmethod
    def run(self) -> None:
        """Process data and populate cache"""
        pass
