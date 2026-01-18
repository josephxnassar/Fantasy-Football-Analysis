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
        
        # Special handling for Statistics with nested structure
        if cls_name == "Statistics" and 'averaged' in cache:
            # Save averaged stats
            for key, df in cache['averaged'].items():
                table_name = f"{cls_name}_averaged_{key}"
                self.db.save_table(table_name, df)
            
            # Save seasonal stats
            for season, season_data in cache.get('by_year', {}).items():
                for key, df in season_data.items():
                    table_name = f"{cls_name}_{season}_{key}"
                    self.db.save_table(table_name, df)
            
            # Save metadata (available seasons)
            if 'available_seasons' in cache:
                metadata_table = f"{cls_name}_metadata"
                metadata_df = pd.DataFrame({'available_seasons': cache['available_seasons']})
                self.db.save_table(metadata_table, metadata_df, index=False)
        else:
            # Standard handling for other data sources
            for key, df in cache.items():
                table_name = f"{cls_name}_{key}"
                self.db.save_table(table_name, df)

    def load_from_db(self, keys: list, cls_name: str) -> dict:
        # Special handling for Statistics
        if cls_name == "Statistics":
            return self._load_statistics_cache()
        
        # Standard handling for other data sources
        data = {}
        for key in keys:
            table_name = f"{cls_name}_{key}"
            if self.db.table_exists(table_name):
                try:
                    data[key] = self.db.load_table(table_name).set_index(key)
                except Exception as e:
                    logger.error(f"Error loading table '{table_name}': {e}")
            else:
                logger.warning(f"Table '{table_name}' does not exist in database.")
        return data
    
    def _load_statistics_cache(self) -> dict:
        """Load Statistics cache with nested structure"""
        cache = {}
        
        # Load metadata to get available seasons
        metadata_table = "Statistics_metadata"
        available_seasons = []
        if self.db.table_exists(metadata_table):
            try:
                metadata_df = self.db.load_table(metadata_table)
                available_seasons = metadata_df['available_seasons'].tolist()
                cache['available_seasons'] = available_seasons
            except Exception as e:
                logger.error(f"Error loading Statistics metadata: {e}")
        
        # Load averaged stats
        averaged_stats = {}
        for pos in constants.POSITIONS:
            table_name = f"Statistics_averaged_{pos}"
            if self.db.table_exists(table_name):
                try:
                    averaged_stats[pos] = self.db.load_table(table_name).set_index(pos)
                except Exception as e:
                    logger.error(f"Error loading table '{table_name}': {e}")
        
        if averaged_stats:
            cache['averaged'] = averaged_stats
        
        # Load seasonal stats
        by_year = {}
        for season in available_seasons:
            season_data = {}
            for pos in constants.POSITIONS:
                table_name = f"Statistics_{season}_{pos}"
                if self.db.table_exists(table_name):
                    try:
                        season_data[pos] = self.db.load_table(table_name).set_index(pos)
                    except Exception as e:
                        logger.error(f"Error loading table '{table_name}': {e}")
            if season_data:
                by_year[season] = season_data
        
        if by_year:
            cache['by_year'] = by_year
        
        return cache
    
    def close(self):
        self.db.close()