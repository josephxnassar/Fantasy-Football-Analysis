"""Database cache service helpers."""

from backend.db.dao import CacheDao

class CacheService:
    """Thin service layer over cache DAO operations."""

    def __init__(self, dao: CacheDao) -> None:
        self.dao = dao

    def create_table(self, table_name: str, columns_sql: list[str], primary_key_sql: str | None = None, indexes_sql: list[str] | None = None) -> None:
        """Create one cache table."""
        raise NotImplementedError

    def replace_table(self, table_name: str, rows: list[dict[str, object]], columns: list[str]) -> None:
        """Replace cache rows in one table."""
        raise NotImplementedError

    def load_table(self, table_name: str, filters: dict[str, object] | None = None, order_by: list[str] | None = None) -> list[dict[str, object]]:
        """Load cache rows from one table."""
        raise NotImplementedError

    def create_meta(self, table_name: str, columns_sql: list[str], primary_key_sql: str | None = None) -> None:
        """Create the meta table."""
        raise NotImplementedError

    def replace_meta(self, table_name: str, row: dict[str, object]) -> None:
        """Replace the meta row."""
        raise NotImplementedError

    def load_meta(self, table_name: str) -> dict[str, object]:
        """Load the meta row."""
        raise NotImplementedError
