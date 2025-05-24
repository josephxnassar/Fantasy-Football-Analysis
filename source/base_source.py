import logging

import pandas as pd

from abc import ABC, abstractmethod
from .database.sqlite import SQLiteCacheManager

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

# ╔═══════════════════════ START SAVE ═══════════════════════╗

    @abstractmethod
    def _get_tables(self):
        pass

    def save_to_db(self, db: 'SQLiteCacheManager') -> None:
        if self.cache is None:
            logger.warning(f"No cached data to save — call run() first.")
            return
        for table_name, df in self._get_tables():
            db.save_table(table_name, df)

# ╚════════════════════════ END SAVE ════════════════════════╝

# ╔═══════════════════════ START LOAD ═══════════════════════╗

    @abstractmethod
    def _get_keys(self) -> list:
        pass

    @abstractmethod
    def _get_name(self, key, **kwargs) -> str:
        pass

    def _set_index(self, df, key) -> pd.DataFrame:
        return df.set_index(key)

    def load_from_db(self, db: 'SQLiteCacheManager', **kwargs) -> None:
        data = {}
        for key in self._get_keys():
            table_name = self._get_name(key, **kwargs)
            if db.table_exists(table_name):
                try:
                    df = db.load_table(table_name)
                    data[key] = self._set_index(df, key)
                except Exception as e:
                    logger.error(f"Error loading table '{table_name}': {e}")
            else:
                logger.warning(f"Table '{table_name}' does not exist in database.")
        self.set_cache(data)

# ╚════════════════════════ END LOAD ════════════════════════╝
