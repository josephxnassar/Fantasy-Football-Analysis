import logging

import pandas as pd

from abc import ABC, abstractmethod
from .database.DAO.sqlite_DAO import SQLiteCacheManager

logger = logging.getLogger(__name__)

class BaseSource(ABC):
    def __init__(self, seasons):
        self.cache = {}
        self.seasons = seasons

    def get_cache(self) -> dict:
        return self.cache

    def set_cache(self, cache: dict) -> None:
        self.cache = cache

    @abstractmethod
    def _load(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def run(self) -> None:
        pass
