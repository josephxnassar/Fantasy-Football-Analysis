"""SQLite data access object for cache management"""

import sqlite3
from pathlib import Path
from typing import List

import pandas as pd

from backend.config.settings import DB_PATH

class SQLiteCacheManager:
    """Low-level SQLite operations for cache tables"""
    
    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path: Path = Path(db_path)
        self.conn: sqlite3.Connection = sqlite3.connect(self.db_path)
        self.cursor: sqlite3.Cursor = self.conn.cursor()

    def save_table(self, table_name: str, df: pd.DataFrame, if_exists: str = "replace", index: bool = True) -> None:
        df.to_sql(table_name, self.conn, if_exists=if_exists, index=index)

    def load_table(self, table_name: str) -> pd.DataFrame:
        return pd.read_sql(f"SELECT * FROM {table_name}", self.conn)

    def table_exists(self, table_name: str) -> bool:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [table_name])
        return self.cursor.fetchone() is not None

    def list_tables(self) -> List[str]:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in self.cursor.fetchall()]
    
    def has_tables(self) -> bool:
        """Check if database has any tables"""
        return len(self.list_tables()) > 0

    def drop_table(self, table_name: str) -> None:
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
        
