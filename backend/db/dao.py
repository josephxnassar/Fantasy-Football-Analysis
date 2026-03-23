"""Raw database access helpers."""

from psycopg import sql

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
        """Creates table in DB with given parameters."""
        pass

    def get_data_types(self, columns: list[str], column_types: list[type]) -> list[sql.Composable]:
        """Converts datatypes into native SQL using the map."""
        return [sql.SQL("{} {}").format(sql.Identifier(column), sql.SQL(DATA_TYPE_MAP[column_type])) for column, column_type in zip(columns, column_types)]

    def close(self) -> None:
        """Closes DB connection."""
        self.connection.close()
