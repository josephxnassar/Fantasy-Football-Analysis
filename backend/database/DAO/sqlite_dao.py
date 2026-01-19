import sqlite3
from pathlib import Path
from typing import List

import pandas as pd

class SQLiteCacheManager:
    def __init__(self, db_path: str = "nfl_cache.db"):
        self.db_path: Path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

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

    def drop_table(self, table_name: str) -> None:
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
        
