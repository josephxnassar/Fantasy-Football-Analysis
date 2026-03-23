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

    def _execute_dml(self, query: sql.Composable, data: list[list[object]] | None = None) -> None:
        """Execute for DML operations."""
        try:
            with self.connection.cursor() as cursor:
                if data is None:
                    cursor.execute(query)
                else:
                    cursor.executemany(query, data)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def _execute_dql(self, query: sql.Composable) -> list[dict]:
        """Execute for DQL queryies."""
        try:
            with self.connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query)
                return list(cursor.fetchall())
        except Exception:
            self.connection.rollback()
            raise

    def create_table(self, name: str, columns: list[str], column_types: list[type], primary_key: list[str]) -> None:
        """Create one table."""
        columns_sql = [sql.SQL("{} {}").format(sql.Identifier(column), sql.SQL(DATA_TYPE_MAP[column_type])) for column, column_type in zip(columns, column_types)]
        primary_key_sql = sql.SQL("PRIMARY KEY ({})").format(sql.SQL(", ").join(sql.Identifier(column) for column in primary_key))
        sql_str = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(sql.Identifier(name), sql.SQL(", ").join(columns_sql + [primary_key_sql]))
        self._execute_dml(sql_str)

    def insert_rows(self, name: str, columns: list[str], rows: list[dict]) -> None:
        """Insert rows into one table."""
        sql_str = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(sql.Identifier(name), sql.SQL(", ").join(sql.Identifier(column) for column in columns), sql.SQL(", ").join(sql.Placeholder() for _ in columns))
        data = [[row[column] for column in columns] for row in rows]
        self._execute_dml(sql_str, data)

    def replace_rows(self, name: str, columns: list[str], rows: list[dict]) -> None:
        """Replace all rows in one table."""
        self.truncate_table(name)
        self.insert_rows(name, columns, rows)

    def select_rows(self, name: str) -> list[dict]:
        """Select all rows from one table."""
        sql_str = sql.SQL("SELECT * FROM {}").format(sql.Identifier(name))
        return self._execute_dql(sql_str)

    def select_meta(self, name: str) -> dict:
        """Select one meta row from one table."""
        rows = self.select_rows(name)
        return rows[0] if rows else {}

    def truncate_table(self, name: str) -> None:
        """Remove all rows from one table."""
        sql_str = sql.SQL("TRUNCATE TABLE {}").format(sql.Identifier(name))
        self._execute_dml(sql_str)

    def close(self) -> None:
        """Closes DB connection."""
        self.connection.close()
