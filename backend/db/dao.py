"""Raw database access helpers."""

from psycopg import sql
from psycopg.rows import dict_row

from backend.db.connection import get_connection

DATA_TYPE_MAP = {
    int: "INTEGER",
    float: "DOUBLE PRECISION",
    str: "TEXT",
    bool: "BOOLEAN",
}

class CacheDao:
    """Raw SQL access for cache tables."""

    def __init__(self) -> None:
        """Opens DB connection."""
        self.connection = get_connection()

    def create_table(self, name: str, columns: list[str], column_types: list[type], primary_key: list[str]) -> None:
        """Create one table."""
        columns_sql = [sql.SQL("{} {}").format(sql.Identifier(column), sql.SQL(DATA_TYPE_MAP[column_type])) for column, column_type in zip(columns, column_types)]
        primary_key_sql = [sql.SQL("PRIMARY KEY ({})").format(sql.SQL(", ").join(sql.Identifier(column) for column in primary_key))]
        create_sql = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(sql.Identifier(name), sql.SQL(", ").join(columns_sql + primary_key_sql))
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(create_sql)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def insert_rows(self, name: str, columns: list[str], rows: list[dict]) -> None:
        """Insert rows into one table."""
        data = [[row[column] for column in columns] for row in rows]
        insert_sql = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(sql.Identifier(name), sql.SQL(", ").join(sql.Identifier(column) for column in columns), sql.SQL(", ").join(sql.Placeholder() for _ in columns))
        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(insert_sql, data)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def replace_rows(self, name: str, columns: list[str], rows: list[dict]) -> None:
        """Replace all rows in one table."""
        data = [[row[column] for column in columns] for row in rows]
        truncate_sql = sql.SQL("TRUNCATE TABLE {}").format(sql.Identifier(name))
        insert_sql = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(sql.Identifier(name), sql.SQL(", ").join(sql.Identifier(column) for column in columns), sql.SQL(", ").join(sql.Placeholder() for _ in columns))
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(truncate_sql)
                if data:
                    cursor.executemany(insert_sql, data)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def select_rows(self, name: str) -> list[dict]:
        """Select all rows from one table."""
        select_sql = sql.SQL("SELECT * FROM {}").format(sql.Identifier(name))
        try:
            with self.connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(select_sql)
                return list(cursor.fetchall())
        except Exception:
            self.connection.rollback()
            raise

    def select_meta(self, name: str) -> dict:
        """Select one meta row from one table."""
        select_sql = sql.SQL("SELECT * FROM {} LIMIT 1").format(sql.Identifier(name))
        try:
            with self.connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(select_sql)
                row = cursor.fetchone()
                return row if row else {}
        except Exception:
            self.connection.rollback()
            raise

    def truncate_table(self, name: str) -> None:
        """Remove all rows from one table."""
        truncate_sql = sql.SQL("TRUNCATE TABLE {}").format(sql.Identifier(name))
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(truncate_sql)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def close(self) -> None:
        """Closes DB connection."""
        self.connection.close()
