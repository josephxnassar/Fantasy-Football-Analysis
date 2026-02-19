"""SQLite data access object for cache management"""

import re
import sqlite3
from pathlib import Path
from typing import List

import pandas as pd

from backend.config.settings import DB_PATH

_TABLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

class SQLiteCacheManager:
    """Low-level SQLite operations for cache tables"""
    
    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path: Path = Path(db_path)
        if str(self.db_path) != ":memory:":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: sqlite3.Connection = sqlite3.connect(self.db_path)
        self.cursor: sqlite3.Cursor = self.conn.cursor()

    @staticmethod
    def _validate_table_name(table_name: str) -> str:
        if not isinstance(table_name, str) or not _TABLE_NAME_PATTERN.fullmatch(table_name):
            raise ValueError(f"Invalid table name: {table_name!r}")
        return table_name

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        return f'"{identifier}"'

    def save_table(self, table_name: str, df: pd.DataFrame, if_exists: str = "replace", index: bool = True) -> None:
        safe_name = self._validate_table_name(table_name)
        df.to_sql(safe_name, self.conn, if_exists=if_exists, index=index)

    def load_table(self, table_name: str) -> pd.DataFrame:
        safe_name = self._validate_table_name(table_name)
        return pd.read_sql(f"SELECT * FROM {self._quote_identifier(safe_name)}", self.conn)

    def table_exists(self, table_name: str) -> bool:
        safe_name = self._validate_table_name(table_name)
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [safe_name])
        return self.cursor.fetchone() is not None

    def list_tables(self) -> List[str]:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in self.cursor.fetchall()]

    def drop_table(self, table_name: str) -> None:
        safe_name = self._validate_table_name(table_name)
        self.cursor.execute(f"DROP TABLE IF EXISTS {self._quote_identifier(safe_name)}")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
        
