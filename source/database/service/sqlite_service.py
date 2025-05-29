import logging

from source.database.DAO.sqlite_dao import SQLiteCacheManager

logger = logging.getLogger(__name__)

class SQLService:
    def __init__(self):
        self.db = SQLiteCacheManager()

    def save_to_db(self, cache: dict, cls_name: str) -> None:
        if cache is None:
            logger.warning(f"No cached data to save — call run() first.")
            return
        for key, df in cache.items():
            table_name = f"{cls_name}_{key}"
            self.db.save_table(table_name, df)

    def load_from_db(self, keys: list, cls_name: str) -> None:
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
    
    def close(self):
        self.db.close()