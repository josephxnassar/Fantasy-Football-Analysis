"""Main application orchestrator for data sources and caching."""

from typing import Any

from backend.db.repository import Repository
from backend.depth_chart.nrp import NRPDepthChart
from backend.schedules.schedules import Schedules
from backend.statistics.statistics import Statistics
from backend.util import constants
from backend.util import cache_keys

class App:
    """Orchestrates data fetching, caching, and loading for all sources."""
    
    def __init__(self) -> None:
        self.db = Repository()
        self.caches: dict[str, Any] = {}
        self.primary_keys: dict[str, Any] = {}
        self.seasons = constants.SEASONS

    def run(self, refresh: bool = False) -> None:
        """Load from database or fetch fresh data."""
        if not refresh:
            self.load()
            return

        instances = [(cache_keys.CACHE["DEPTHCHART"], NRPDepthChart(self.seasons)),
                     (cache_keys.CACHE["SCHEDULES"], Schedules(self.seasons)),
                     (cache_keys.CACHE["STATISTICS"], Statistics(self.seasons))]
        
        for cache_name, instance in instances:
            instance.run()
            self.caches[cache_name] = instance.get_cache()
            self.primary_keys[cache_name] = instance.get_primary_keys()

        self.save()

    def load(self) -> None:
        """Load all caches from database."""
        self.caches[cache_keys.CACHE["DEPTHCHART"]] = self.db.load_from_db(cache_keys.CACHE["DEPTHCHART"])
        self.caches[cache_keys.CACHE["SCHEDULES"]] = self.db.load_from_db(cache_keys.CACHE["SCHEDULES"])
        self.caches[cache_keys.CACHE["STATISTICS"]] = self.db.load_from_db(cache_keys.CACHE["STATISTICS"])
        
    def save(self) -> None:
        """Save all caches to database."""
        for name, cache in self.caches.items():
            self.db.save_to_db(name, cache, self.primary_keys[name])
