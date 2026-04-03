"""Unit tests for NRPDepthChart.run."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.depth_chart.nrp import NRPDepthChart
from backend.util.exceptions import DataLoadError, DataProcessingError

# normal

def test_run_builds_expected_cache_from_cleaned_depth_chart(nrp_depth_chart: NRPDepthChart) -> None:
    """run calls helper steps and stores the final depth chart cache."""
    loaded_depth = object()
    cleaned_depth_df = pd.DataFrame([
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "WSH", "pos_abb": "QB", "player_name": "Jayden Daniels", "pos_rank": 1, "pos_slot": 1},
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "WSH", "pos_abb": "QB", "player_name": "Marcus Mariota", "pos_rank": 2, "pos_slot": 1},
    ])
    load_mock = MagicMock(return_value=loaded_depth)
    clean_mock = MagicMock(return_value=cleaned_depth_df)
    set_cache_mock = MagicMock()

    nrp_depth_chart._load_depth_charts = load_mock
    nrp_depth_chart._clean_depth_charts = clean_mock
    nrp_depth_chart.set_cache = set_cache_mock

    nrp_depth_chart.run()

    load_mock.assert_called_once_with()
    clean_mock.assert_called_once_with(loaded_depth)
    set_cache_mock.assert_called_once_with([
        {"team": "WSH", "position": "QB", "position_slot": 1, "starter": "Jayden Daniels", "2nd": "Marcus Mariota", "3rd": None, "4th": None},
    ])

# edge

def test_run_uses_latest_snapshot_per_team_not_global_snapshot(nrp_depth_chart: NRPDepthChart) -> None:
    """run keeps the latest snapshot for each team instead of one global snapshot."""
    cleaned_depth_df = pd.DataFrame([
        {"dt": pd.Timestamp("2025-08-30", tz="UTC"), "team": "WSH", "pos_abb": "QB", "player_name": "Old Starter", "pos_rank": 1, "pos_slot": 1},
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "WSH", "pos_abb": "QB", "player_name": "Jayden Daniels", "pos_rank": 1, "pos_slot": 1},
        {"dt": pd.Timestamp("2025-08-31", tz="UTC"), "team": "LAR", "pos_abb": "QB", "player_name": "Matthew Stafford", "pos_rank": 1, "pos_slot": 1},
    ])
    nrp_depth_chart._load_depth_charts = MagicMock(return_value=object())
    nrp_depth_chart._clean_depth_charts = MagicMock(return_value=cleaned_depth_df)
    set_cache_mock = MagicMock()
    nrp_depth_chart.set_cache = set_cache_mock

    nrp_depth_chart.run()

    set_cache_mock.assert_called_once_with([
        {"team": "WSH", "position": "QB", "position_slot": 1, "starter": "Jayden Daniels", "2nd": None, "3rd": None, "4th": None},
        {"team": "LAR", "position": "QB", "position_slot": 1, "starter": "Matthew Stafford", "2nd": None, "3rd": None, "4th": None},
    ])

def test_run_limits_each_slot_to_four_unique_players(nrp_depth_chart: NRPDepthChart) -> None:
    """run keeps only the first four unique players for a slot."""
    cleaned_depth_df = pd.DataFrame([
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "WSH", "pos_abb": "RB", "player_name": "Player 1", "pos_rank": 1, "pos_slot": 1},
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "WSH", "pos_abb": "RB", "player_name": "Player 2", "pos_rank": 2, "pos_slot": 1},
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "WSH", "pos_abb": "RB", "player_name": "Player 3", "pos_rank": 3, "pos_slot": 1},
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "WSH", "pos_abb": "RB", "player_name": "Player 4", "pos_rank": 4, "pos_slot": 1},
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "WSH", "pos_abb": "RB", "player_name": "Player 5", "pos_rank": 5, "pos_slot": 1},
    ])
    nrp_depth_chart._load_depth_charts = MagicMock(return_value=object())
    nrp_depth_chart._clean_depth_charts = MagicMock(return_value=cleaned_depth_df)
    set_cache_mock = MagicMock()
    nrp_depth_chart.set_cache = set_cache_mock

    nrp_depth_chart.run()

    set_cache_mock.assert_called_once_with([
        {"team": "WSH", "position": "RB", "position_slot": 1, "starter": "Player 1", "2nd": "Player 2", "3rd": "Player 3", "4th": "Player 4"},
    ])

# exception

def test_run_raises_data_processing_error_when_load_depth_charts_fails(nrp_depth_chart: NRPDepthChart) -> None:
    """run wraps _load_depth_charts failures in DataProcessingError."""
    nrp_depth_chart._load_depth_charts = MagicMock(side_effect=DataLoadError("dummy", source="NRPDepthChart"))

    with pytest.raises(DataProcessingError, match="Failed to build depth charts: dummy") as exc_info:
        nrp_depth_chart.run()

    assert exc_info.value.source == "NRPDepthChart"

def test_run_raises_data_processing_error_when_clean_depth_charts_fails(nrp_depth_chart: NRPDepthChart) -> None:
    """run wraps _clean_depth_charts failures in DataProcessingError."""
    nrp_depth_chart._load_depth_charts = MagicMock(return_value=object())
    nrp_depth_chart._clean_depth_charts = MagicMock(side_effect=DataProcessingError("dummy", source="NRPDepthChart"))

    with pytest.raises(DataProcessingError, match="Failed to build depth charts: dummy") as exc_info:
        nrp_depth_chart.run()

    assert exc_info.value.source == "NRPDepthChart"
