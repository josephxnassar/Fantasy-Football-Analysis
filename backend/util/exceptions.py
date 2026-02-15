"""Custom exception hierarchy for the Fantasy Football backend.

Hierarchy:
    FantasyFootballError (base)
    ├── DataLoadError           — external data source failures (nflreadpy, web)
    ├── DataProcessingError     — data transformation or computation failures
    ├── ScrapingError           — ESPN web scraping failures
    ├── CacheNotLoadedError     — cache missing or empty
    └── PlayerNotFoundError     — player lookup failed across all data sources
"""

class FantasyFootballError(Exception):
    """Base exception for all Fantasy Football backend errors"""

    def __init__(self, message: str, source: str = "") -> None:
        self.source: str = source
        super().__init__(message)

class DataLoadError(FantasyFootballError):
    """Failed to load data from an external source (nflreadpy, file system)"""
    pass

class DataProcessingError(FantasyFootballError):
    """Failed during data transformation, aggregation, or computation"""
    pass

class ScrapingError(FantasyFootballError):
    """Failed to scrape or parse web data (ESPN depth charts)"""
    pass

class CacheNotLoadedError(FantasyFootballError):
    """Required cache data is not loaded or is empty"""
    pass

class PlayerNotFoundError(FantasyFootballError):
    """Player could not be found in any data source"""
    pass
