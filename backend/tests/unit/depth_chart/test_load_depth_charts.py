"""Unit tests for NRPDepthChart._load_depth_charts."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.depth_chart import nrp as nrp_module
from backend.depth_chart.nrp import NRPDepthChart
from backend.util.exceptions import DataLoadError

# normal

def test_load_depth_charts_selects_normalizes_and_filters_positions(nrp_depth_chart: NRPDepthChart, monkeypatch: pytest.MonkeyPatch) -> None:
    """_load_depth_charts keeps required columns, normalizes teams, and filters positions."""
    imported_depth_df = pd.DataFrame([
        {"dt": "2025-09-01", "team": "LA", "pos_abb": "QB", "player_name": "Matthew Stafford", "pos_rank": "1", "pos_slot": "1", "extra": "ignore"},
        {"dt": "2025-09-01", "team": "OAK", "pos_abb": "RB", "player_name": "Zamir White", "pos_rank": "1", "pos_slot": "1", "extra": "ignore"},
        {"dt": "2025-09-01", "team": "WAS", "pos_abb": "WR", "player_name": "Terry McLaurin", "pos_rank": "1", "pos_slot": "1", "extra": "ignore"},
    ])
    mock_result = MagicMock()
    mock_result.to_pandas.return_value = imported_depth_df
    monkeypatch.setattr(nrp_module.nfl, "load_depth_charts", lambda seasons: mock_result)

    loaded = nrp_depth_chart._load_depth_charts()

    assert list(loaded.columns) == ["dt", "team", "pos_abb", "player_name", "pos_rank", "pos_slot"]
    assert loaded.to_dict("records") == [
        {"dt": pd.Timestamp("2025-09-01 00:00:00+0000", tz="UTC"), "team": "LAR", "pos_abb": "QB", "player_name": "Matthew Stafford", "pos_rank": 1, "pos_slot": 1},
        {"dt": pd.Timestamp("2025-09-01 00:00:00+0000", tz="UTC"), "team": "LV", "pos_abb": "RB", "player_name": "Zamir White", "pos_rank": 1, "pos_slot": 1},
    ]

def test_load_depth_charts_converts_datetime_and_numeric_columns(nrp_depth_chart: NRPDepthChart, monkeypatch: pytest.MonkeyPatch) -> None:
    """_load_depth_charts converts datetime and numeric columns."""
    imported_depth_df = pd.DataFrame([
        {"dt": "2025-09-03T12:30:00", "team": "LAR", "pos_abb": "QB", "player_name": "Matthew Stafford", "pos_rank": "2", "pos_slot": "3"},
    ])
    mock_result = MagicMock()
    mock_result.to_pandas.return_value = imported_depth_df
    monkeypatch.setattr(nrp_module.nfl, "load_depth_charts", lambda seasons: mock_result)

    loaded = nrp_depth_chart._load_depth_charts()

    assert loaded.loc[0, "dt"] == pd.Timestamp("2025-09-03 12:30:00+0000", tz="UTC")
    assert loaded.loc[0, "pos_rank"] == 2
    assert loaded.loc[0, "pos_slot"] == 3

# edge

def test_load_depth_charts_coerces_invalid_datetime_and_numeric_values_to_missing(nrp_depth_chart: NRPDepthChart, monkeypatch: pytest.MonkeyPatch) -> None:
    """_load_depth_charts coerces invalid datetime and numeric values to missing."""
    imported_depth_df = pd.DataFrame([
        {"dt": "bad-date", "team": "LAR", "pos_abb": "QB", "player_name": "Matthew Stafford", "pos_rank": "bad-rank", "pos_slot": "bad-slot"},
    ])
    mock_result = MagicMock()
    mock_result.to_pandas.return_value = imported_depth_df
    monkeypatch.setattr(nrp_module.nfl, "load_depth_charts", lambda seasons: mock_result)

    loaded = nrp_depth_chart._load_depth_charts()

    assert pd.isna(loaded.loc[0, "dt"])
    assert pd.isna(loaded.loc[0, "pos_rank"])
    assert pd.isna(loaded.loc[0, "pos_slot"])

def test_load_depth_charts_uses_current_season_for_import(nrp_depth_chart: NRPDepthChart, monkeypatch: pytest.MonkeyPatch) -> None:
    """_load_depth_charts imports only the current season."""
    mock_result = MagicMock()
    mock_result.to_pandas.return_value = pd.DataFrame(columns=["dt", "team", "pos_abb", "player_name", "pos_rank", "pos_slot"])
    load_mock = MagicMock(return_value=mock_result)
    monkeypatch.setattr(nrp_module.nfl, "load_depth_charts", load_mock)

    nrp_depth_chart._load_depth_charts()

    load_mock.assert_called_once_with(seasons=2025)

# exception

def test_load_depth_charts_raises_data_load_error_on_import_failure(nrp_depth_chart: NRPDepthChart, monkeypatch: pytest.MonkeyPatch) -> None:
    """_load_depth_charts wraps upstream failures in DataLoadError."""
    def raise_error(seasons: int) -> None:
        raise RuntimeError("dummy")

    monkeypatch.setattr(nrp_module.nfl, "load_depth_charts", raise_error)

    with pytest.raises(DataLoadError, match="Failed to load depth charts from nflreadpy: dummy") as exc_info:
        nrp_depth_chart._load_depth_charts()

    assert exc_info.value.source == "NRPDepthChart"
