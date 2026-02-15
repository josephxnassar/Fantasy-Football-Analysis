"""Main application orchestrator for data sources and caching"""

from typing import Any, Dict

from backend.database.service.sqlite_service import SQLService
from backend.depth_chart.espn import ESPNDepthChart
from backend.schedules.schedules import Schedules
from backend.statistics.statistics import Statistics
from backend.util import constants

class App:
    """Orchestrates data fetching, caching, and loading for all sources"""
    
    def __init__(self) -> None:
        self.db: SQLService = SQLService()
        self.caches: Dict[str, Any] = {}
    
    def initialize(self) -> None:
        """Load from cache or fetch fresh data if cache doesn't exist"""
        if self.db.has_cached_data():
            self.load()
        else:
            self.run()
            self.save()
    
    def run(self) -> None:
        """Fetch fresh data from all sources"""
        instances = [ESPNDepthChart(), 
                     Schedules(constants.SEASONS), 
                     Statistics(constants.SEASONS)]

        for instance in instances:
            instance.run()
            self.caches[instance.__class__.__name__] = instance.get_cache()
    
    def save(self) -> None:
        """Save all caches to database"""
        for name, cache in self.caches.items():
            self.db.save_to_db(cache, name)

    def load(self) -> None:
        """Load all caches from database"""
        instances = [ESPNDepthChart.__new__(ESPNDepthChart), 
                     Schedules.__new__(Schedules), 
                     Statistics.__new__(Statistics)]
        
        for instance in instances:
            name = instance.__class__.__name__
            self.caches[name] = self.db.load_from_db(instance.get_keys(), name)
