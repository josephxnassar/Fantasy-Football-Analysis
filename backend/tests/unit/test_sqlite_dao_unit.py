import pandas as pd
import pytest

from backend.database.DAO.sqlite_dao import SQLiteCacheManager

pytestmark = pytest.mark.unit

def test_sqlite_dao_rejects_unsafe_table_names() -> None:
    manager = SQLiteCacheManager(":memory:")
    df = pd.DataFrame({"value": [1]})
    unsafe_name = "stats; DROP TABLE users;--"

    try:
        with pytest.raises(ValueError):
            manager.save_table(unsafe_name, df, index=False)
        with pytest.raises(ValueError):
            manager.load_table(unsafe_name)
        with pytest.raises(ValueError):
            manager.table_exists(unsafe_name)
        with pytest.raises(ValueError):
            manager.drop_table(unsafe_name)
    finally:
        manager.close()

def test_sqlite_dao_allows_valid_table_names() -> None:
    manager = SQLiteCacheManager(":memory:")
    table_name = "stats_2025_QB"
    source = pd.DataFrame({"player": ["Patrick Mahomes"], "pass_yds": [4280]})

    try:
        manager.save_table(table_name, source, index=False)
        loaded = manager.load_table(table_name)

        assert manager.table_exists(table_name) is True
        assert loaded.to_dict("records") == source.to_dict("records")

        manager.drop_table(table_name)
        assert manager.table_exists(table_name) is False
    finally:
        manager.close()
