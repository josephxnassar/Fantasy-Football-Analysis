"""Main application orchestrator for data sources and caching"""

import logging
from typing import Any, Dict

from backend.depth_chart.nrp import NRPDepthChart
from backend.schedules.schedules import Schedules
from backend.statistics.statistics import Statistics
from backend.util import constants

logger = logging.getLogger(__name__)


class App:
    """Orchestrates data fetching, caching, and loading for all sources"""
    
    def __init__(self) -> None:
        self.caches: Dict[str, Any] = {}
