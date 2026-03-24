"""Raw database access helpers."""

from typing import Any

from psycopg import sql
from psycopg.rows import dict_row

from backend.db.connection import get_connection

class CacheDao:
    """Raw SQL access for cache tables."""

    def __init__(self) -> None:
        """Opens DB connection."""
        self.connection = get_connection()

    def table_exists(self, table_name: str) -> bool:
        """Return whether one table exists."""
        select_string = "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(select_string, [table_name])
                exists = bool(cursor.fetchone()[0])
            self.connection.commit()
            return exists
        except Exception:
            self.connection.rollback()
            raise

    def create_table(self, table_name: str, columns: list[str], data_types: list[str], primary_keys: list[str]) -> None:
        """Create one table."""
        create_string = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({}, PRIMARY KEY ({}))").format(sql.Identifier(table_name), sql.SQL(", ").join(sql.SQL("{} {}").format(sql.Identifier(column), sql.SQL(data_type)) for column, data_type in zip(columns, data_types)), sql.SQL(", ").join(sql.Identifier(column) for column in primary_keys))
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(create_string)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def insert_rows(self, table_name: str, columns: list[str], data: list[list[Any]]) -> None:
        """Insert rows into one table."""
        insert_string = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(sql.Identifier(table_name), sql.SQL(", ").join(sql.Identifier(column) for column in columns), sql.SQL(", ").join(sql.Placeholder() for _ in columns))
        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(insert_string, data)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def truncate_table(self, table_name: str) -> None:
        """Remove all rows from one table."""
        truncate_string = sql.SQL("TRUNCATE TABLE {}").format(sql.Identifier(table_name))
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(truncate_string)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def load_table(self, table_name: str) -> list[dict]:
        """Load one table."""
        select_string = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
        try:
            with self.connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(select_string)
                rows = list(cursor.fetchall())
            self.connection.commit()
            return rows
        except Exception:
            self.connection.rollback()
            raise

    def close(self) -> None:
        """Closes DB connection."""
        self.connection.close()
