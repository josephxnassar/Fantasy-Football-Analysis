"""Database cache service helpers."""

from typing import Any

import pandas as pd

from backend.db.dao import CacheDao
from backend.util import cache_keys

DATA_TYPE_MAP = {
    int: "INTEGER",
    float: "DOUBLE PRECISION",
    str: "TEXT",
    bool: "BOOLEAN",
    pd.Timestamp: "TIMESTAMP",
}

class Repository:
    """Thin service layer over cache DAO operations."""

    def __init__(self) -> None:
        """Initialize DAO instance."""
        self.dao = CacheDao()

    def save_to_db(self, cache_name: str, cache: Any, primary_keys: Any):
        """Save one top-level cache to the database."""
        if cache_name == cache_keys.CACHE["STATISTICS"]:
            for name, table in cache.items():
                if name == cache_keys.STATS["META"]:
                    meta_table = [{"key": name, **table}]
                    self.save_table(name, meta_table, primary_keys[name])
                else:
                    self.save_table(name, cache[name], primary_keys[name])
        else:
            self.save_table(cache_name, cache, primary_keys)

    def save_table(self, cache_name: str, cache: Any, primary_keys: Any) -> None:
        """Save one cache to the database."""
        columns = list(cache[0].keys())
        data_types = [DATA_TYPE_MAP[type(next((row[column] for row in cache if row[column] is not None), ""))] for column in columns]

        if self.dao.table_exists(cache_name):
            self.dao.truncate_table(cache_name)
        else:
            self.dao.create_table(cache_name, columns, data_types, primary_keys)
        
        rows = [[None if row[column] is pd.NaT else row[column] for column in columns] for row in cache]
        self.dao.insert_rows(cache_name, columns, rows)

    def load_from_db(self, cache_name: str):
        """Load one top-level cache from the database."""
        if cache_name == cache_keys.CACHE["STATISTICS"]:
            stats: dict[str, Any] = {}
            for name in cache_keys.STATS.values():
                if name == cache_keys.STATS["META"]:
                    meta = self.load_table(name)
                    stats[name] = meta[0] if meta else {}
                    stats[name].pop("key", None)
                else:
                    stats[name] = self.load_table(name)
            return stats
        else:
            return self.load_table(cache_name)

    def load_table(self, cache_name: str) -> list[dict]:
        """Load one cache table."""
        if not self.dao.table_exists(cache_name):
            return []
        return self.dao.load_table(cache_name)

    def close(self) -> None:
        """Close the DAO connection."""
        self.dao.close()
