from typing import Dict, Any

from backend.database.service import SQLService
from backend.depth_chart import ESPNDepthChart
from backend.schedules import Schedules
from backend.statistics import Statistics
from backend.util import constants

class App:
    def __init__(self) -> None:
        self.db: SQLService = SQLService()
        self.caches: Dict[str, Any] = {}
    
    def run(self) -> None:
        instances = [ESPNDepthChart(), 
                     Schedules([constants.CURRENT_SEASON]), 
                     Statistics(constants.STATISTICS_SEASONS)]

        for instance in instances:
            instance.run()
            self.caches[instance.__class__.__name__] = instance.get_cache()
    
    def save(self) -> None:
        for name, cache in self.caches.items():
            self.db.save_to_db(cache, name)

    def load(self) -> None:
        instances = [ESPNDepthChart.__new__(ESPNDepthChart), Schedules.__new__(Schedules), Statistics.__new__(Statistics)]
        
        for instance in instances:
            name = instance.__class__.__name__
            self.caches[name] = self.db.load_from_db(instance.get_keys(), name)