import logging
from typing import Dict, List, Any

import pandas as pd

from abc import ABC, abstractmethod
from backend.util import constants

logger = logging.getLogger(__name__)

class BaseSource(ABC):
    def __init__(self, seasons: List[int]):
        self.cache: Dict[str, Any] = {}
        self.seasons: List[int] = seasons

    def get_keys(self) -> List[str]:
        return constants.TEAMS

    def get_cache(self) -> Dict[str, Any]:
        return self.cache

    def set_cache(self, cache: Dict[str, Any]) -> None:
        self.cache = cache

    @abstractmethod
    def _load(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def run(self) -> None:
        pass
