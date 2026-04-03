"""Unit tests for NRPDepthChart._clean_depth_charts."""

import pandas as pd
import pytest

from backend.depth_chart.nrp import NRPDepthChart
from backend.util.exceptions import DataProcessingError

# normal

def test_clean_depth_charts_drops_missing_rows_and_blank_names(nrp_depth_chart: NRPDepthChart) -> None:
    """_clean_depth_charts drops rows missing required values and blank names."""
    depth_df = pd.DataFrame([
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "LAR", "pos_abb": "QB", "player_name": "Matthew Stafford", "pos_rank": 1.0, "pos_slot": 1.0},
        {"dt": pd.NaT, "team": "LAR", "pos_abb": "QB", "player_name": "Jimmy Garoppolo", "pos_rank": 2.0, "pos_slot": 1.0},
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "LAR", "pos_abb": "QB", "player_name": "   ", "pos_rank": 3.0, "pos_slot": 1.0},
    ])

    cleaned = nrp_depth_chart._clean_depth_charts(depth_df)

    assert cleaned.to_dict("records") == [
        {"dt": pd.Timestamp("2025-09-01 00:00:00+0000", tz="UTC"), "team": "LAR", "pos_abb": "QB", "player_name": "Matthew Stafford", "pos_rank": 1, "pos_slot": 1},
    ]

def test_clean_depth_charts_strips_names_converts_to_int_and_sorts(nrp_depth_chart: NRPDepthChart) -> None:
    """_clean_depth_charts strips names, converts numeric columns to int, and sorts rows."""
    depth_df = pd.DataFrame([
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "LV", "pos_abb": "RB", "player_name": "  Zamir White  ", "pos_rank": 2.0, "pos_slot": 2.0},
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "LAR", "pos_abb": "QB", "player_name": "Matthew Stafford", "pos_rank": 1.0, "pos_slot": 1.0},
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "LV", "pos_abb": "RB", "player_name": "Alexander Mattison", "pos_rank": 1.0, "pos_slot": 2.0},
    ])

    cleaned = nrp_depth_chart._clean_depth_charts(depth_df)

    assert cleaned[["team", "pos_abb", "pos_slot", "pos_rank", "player_name"]].to_dict("records") == [
        {"team": "LAR", "pos_abb": "QB", "pos_slot": 1, "pos_rank": 1, "player_name": "Matthew Stafford"},
        {"team": "LV", "pos_abb": "RB", "pos_slot": 2, "pos_rank": 1, "player_name": "Alexander Mattison"},
        {"team": "LV", "pos_abb": "RB", "pos_slot": 2, "pos_rank": 2, "player_name": "Zamir White"},
    ]
    assert cleaned["pos_rank"].tolist() == [1, 1, 2]
    assert cleaned["pos_slot"].tolist() == [1, 2, 2]

# edge

def test_clean_depth_charts_drops_duplicate_rows(nrp_depth_chart: NRPDepthChart) -> None:
    """_clean_depth_charts drops duplicate depth chart rows."""
    depth_df = pd.DataFrame([
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "LAR", "pos_abb": "QB", "player_name": "Matthew Stafford", "pos_rank": 1.0, "pos_slot": 1.0},
        {"dt": pd.Timestamp("2025-09-02", tz="UTC"), "team": "LAR", "pos_abb": "QB", "player_name": "Matthew Stafford", "pos_rank": 1.0, "pos_slot": 1.0},
    ])

    cleaned = nrp_depth_chart._clean_depth_charts(depth_df)

    assert cleaned.to_dict("records") == [
        {"dt": pd.Timestamp("2025-09-01 00:00:00+0000", tz="UTC"), "team": "LAR", "pos_abb": "QB", "player_name": "Matthew Stafford", "pos_rank": 1, "pos_slot": 1},
    ]

# exception

def test_clean_depth_charts_raises_data_processing_error_for_missing_required_column(nrp_depth_chart: NRPDepthChart) -> None:
    """_clean_depth_charts wraps malformed input in DataProcessingError."""
    malformed_depth_df = pd.DataFrame([
        {"dt": pd.Timestamp("2025-09-01", tz="UTC"), "team": "LAR", "player_name": "Matthew Stafford", "pos_rank": 1.0, "pos_slot": 1.0},
    ])

    with pytest.raises(DataProcessingError, match="Failed to clean depth charts") as exc_info:
        nrp_depth_chart._clean_depth_charts(malformed_depth_df)

    assert exc_info.value.source == "NRPDepthChart"
