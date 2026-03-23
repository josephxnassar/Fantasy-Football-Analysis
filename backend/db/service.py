"""Database cache service helpers."""

from backend.db.dao import CacheDao

class CacheService:
    """Thin service layer over cache DAO operations."""

    def __init__(self, dao: CacheDao) -> None:
        """Initialize DAO instance."""
        self.dao = dao
