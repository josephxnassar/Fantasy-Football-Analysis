"""Database cache service helpers."""

from backend.db.dao import CacheDao

class CacheService:
    """Thin service layer over cache DAO operations."""

    def __init__(self, dao: CacheDao) -> None:
        """Initialize DAO instance."""
        self.dao = dao

    def create_table(self, name: str, columns: list[str], column_types: list[type], primary_key: list[str]) -> None:
        """Create one table."""
        self.dao.create_table(name, columns, column_types, primary_key)

    def insert_rows(self, name: str, columns: list[str], rows: list[dict]) -> None:
        """Insert rows into one table."""
        self.dao.insert_rows(name, columns, rows)

    def replace_rows(self, name: str, columns: list[str], rows: list[dict]) -> None:
        """Replace all rows in one table."""
        self.dao.replace_rows(name, columns, rows)

    def select_rows(self, name: str) -> list[dict]:
        """Select all rows from one table."""
        return self.dao.select_rows(name)

    def select_meta(self, name: str) -> dict:
        """Select one meta row from one table."""
        return self.dao.select_meta(name)
    
    def truncate_table(self, name: str) -> None:
        """Remove all rows from one table."""
        self.dao.truncate_table(name)

    def close(self) -> None:
        """Close the DAO connection."""
        self.dao.close()
