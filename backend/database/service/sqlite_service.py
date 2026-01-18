import logging
import pandas as pd

from backend.database.DAO import SQLiteCacheManager
from backend.util import constants

logger = logging.getLogger(__name__)

class SQLService:
    def __init__(self):
        self.db = SQLiteCacheManager()

    def save_to_db(self, cache: dict, cls_name: str) -> None:
        if cache is None:
            logger.warning(f"No cached data to save — call run() first.")
            return
        
        if cls_name == "Statistics" and 'averaged' in cache:
            self._save_statistics_cache(cache, cls_name)
        else:
            self._save_standard_cache(cache, cls_name)

    def _save_standard_cache(self, cache: dict, cls_name: str) -> None:
        """Save standard cache structure"""
        for key, df in cache.items():
            self.db.save_table(f"{cls_name}_{key}", df)

    def _save_statistics_cache(self, cache: dict, cls_name: str) -> None:
        """Save Statistics cache with nested structure"""
        # Save averaged stats
        for key, df in cache['averaged'].items():
            self.db.save_table(f"{cls_name}_averaged_{key}", df)
        
        # Save seasonal stats
        for season, season_data in cache.get('by_year', {}).items():
            for key, df in season_data.items():
                self.db.save_table(f"{cls_name}_{season}_{key}", df)
        
        # Save metadata
        if 'available_seasons' in cache:
            metadata_df = pd.DataFrame({'available_seasons': cache['available_seasons']})
            self.db.save_table(f"{cls_name}_metadata", metadata_df, index=False)

    def load_from_db(self, keys: list, cls_name: str) -> dict:
        if cls_name == "Statistics":
            return self._load_statistics_cache()
        return self._load_standard_cache(keys, cls_name)
    
    def _load_standard_cache(self, keys: list, cls_name: str) -> dict:
        """Load standard cache structure"""
        data = {}
        for key in keys:
            table_name = f"{cls_name}_{key}"
            df = self._load_table_safe(table_name)
            if df is not None:
                data[key] = df.set_index(key)
        return data

    def _load_table_safe(self, table_name: str) -> pd.DataFrame:
        """Load table if it exists, return None otherwise"""
        if not self.db.table_exists(table_name):
            return None
        try:
            return self.db.load_table(table_name)
        except Exception as e:
            logger.error(f"Error loading table '{table_name}': {e}")
            return None
    
    def _load_statistics_cache(self) -> dict:
        """Load Statistics cache with nested structure"""
        cache = {}
        
        # Load metadata
        metadata_df = self._load_table_safe("Statistics_metadata")
        available_seasons = []
        if metadata_df is not None:
            available_seasons = metadata_df['available_seasons'].tolist()
            cache['available_seasons'] = available_seasons
        
        # Load averaged stats
        averaged_stats = {
            pos: df.set_index(pos)
            for pos in constants.POSITIONS
            if (df := self._load_table_safe(f"Statistics_averaged_{pos}")) is not None
        }
        if averaged_stats:
            cache['averaged'] = averaged_stats
        
        # Load seasonal stats
        by_year = {}
        for season in available_seasons:
            season_data = {
                pos: df.set_index(pos)
                for pos in constants.POSITIONS
                if (df := self._load_table_safe(f"Statistics_{season}_{pos}")) is not None
            }
            if season_data:
                by_year[season] = season_data
        
        if by_year:
            cache['by_year'] = by_year
        
        return cache
    
    def close(self):
        self.db.close()