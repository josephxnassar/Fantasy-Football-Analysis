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

# ═══════════════════ ❖  DATABASE OPERATIONS  ❖ ═══════════════════

    @abstractmethod
    def _get_name(self, key) -> str:
        pass

    @abstractmethod
    def _get_keys(self) -> list:
        pass

    def save_to_db(self, db: 'SQLiteCacheManager') -> None:
        if self.cache is None:
            logger.warning(f"No cached data to save — call run() first.")
            return
        for key, df in self.cache.items():
            table_name = self._get_name(key)
            db.save_table(table_name, df)

    def load_from_db(self, db: SQLiteCacheManager) -> None:
        data = {}
        for key in self._get_keys():
            table_name = self._get_name(key)
            if db.table_exists(table_name):
                try:
                    data[key] = db.load_table(table_name).set_index(key)
                except Exception as e:
                    logger.error(f"Error loading table '{table_name}': {e}")
            else:
                logger.warning(f"Table '{table_name}' does not exist in database.")
        self.set_cache(data)
