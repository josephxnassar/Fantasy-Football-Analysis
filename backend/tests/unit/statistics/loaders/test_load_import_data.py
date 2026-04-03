"""Unit tests for StatisticsSourceLoader.load_import_data."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.statistics.loaders import StatisticsSourceLoader

# normal

def test_load_import_data_returns_results_for_all_loader_outputs(statistics_loader: StatisticsSourceLoader) -> None:
    """load_import_data returns a dict of all imported source frames."""
    rosters_df = pd.DataFrame([{"player": "A"}])
    weekly_df = pd.DataFrame([{"player": "B"}])

    statistics_loader.load_ff_playerid_map = MagicMock(return_value={"staffma01": "00-0034860"})
    statistics_loader._build_import_loader_map = MagicMock(return_value={
        "rosters": lambda: rosters_df,
        "player_weekly": lambda: weekly_df,
    })

    results = statistics_loader.load_import_data()

    assert statistics_loader._build_import_loader_map.call_args.args[0] == {"staffma01": "00-0034860"}
    assert results["rosters"].equals(rosters_df)
    assert results["player_weekly"].equals(weekly_df)

# exception

def test_load_import_data_propagates_loader_failure(statistics_loader: StatisticsSourceLoader) -> None:
    """load_import_data propagates a failing loader exception."""
    def raise_error() -> pd.DataFrame:
        raise RuntimeError("dummy")

    statistics_loader.load_ff_playerid_map = MagicMock(return_value={})
    statistics_loader._build_import_loader_map = MagicMock(return_value={
        "rosters": lambda: pd.DataFrame([{"player": "A"}]),
        "player_weekly": raise_error,
    })

    with pytest.raises(RuntimeError, match="dummy"):
        statistics_loader.load_import_data()
