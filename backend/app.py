"""Main application orchestrator for data sources and caching"""

import logging
from typing import Any, Dict

from backend.config.settings import DEPTH_CHART_SOURCE
from backend.database.service.sqlite_service import SQLService
from backend.depth_chart.espn import ESPNDepthChart
from backend.depth_chart.nrp import NRPDepthChart
from backend.schedules.schedules import Schedules
from backend.statistics.statistics import Statistics
from backend.util import constants

logger = logging.getLogger(__name__)

class App:
    """Orchestrates data fetching, caching, and loading for all sources"""
    
    def __init__(self) -> None:
        self.db: SQLService = SQLService()
        self.caches: Dict[str, Any] = {}
    
    def initialize(self) -> None:
        """Load cached data when available, otherwise fetch and persist fresh data."""
        if self.db.has_cached_data():
            self.load()
            return

        logger.info("Cache tables missing; fetching fresh data and rebuilding cache.")
        self.run()
        self.save()

    def _get_depth_chart_source(self):
        source = DEPTH_CHART_SOURCE
        if source == "nrp":
            return NRPDepthChart()
        if source == "espn":
            return ESPNDepthChart()
        logger.warning("Unknown DEPTH_CHART_SOURCE '%s'; defaulting to 'espn'.", source)
        return ESPNDepthChart()
    
    def run(self) -> None:
        """Fetch fresh data from all sources"""
        instances = [(constants.CACHE["DEPTH_CHART"], self._get_depth_chart_source()),
                     (constants.CACHE["SCHEDULES"], Schedules(constants.SEASONS)),
                     (constants.CACHE["STATISTICS"], Statistics(constants.SEASONS))]

        for cache_name, instance in instances:
            instance.run()
            self.caches[cache_name] = instance.get_cache()
    
    def save(self) -> None:
        """Save all caches to database"""
        for name, cache in self.caches.items():
            self.db.save_to_db(cache, name)

    def load(self) -> None:
        """Load all caches from database"""
        self.caches[constants.CACHE["DEPTH_CHART"]] = self.db.load_from_db(constants.TEAMS, constants.CACHE["DEPTH_CHART"])
        self.caches[constants.CACHE["SCHEDULES"]] = self.db.load_from_db(constants.TEAMS, constants.CACHE["SCHEDULES"])
        self.caches[constants.CACHE["STATISTICS"]] = self.db.load_from_db(constants.POSITIONS, constants.CACHE["STATISTICS"])
