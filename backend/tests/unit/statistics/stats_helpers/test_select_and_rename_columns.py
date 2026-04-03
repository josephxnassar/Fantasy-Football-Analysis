"""Unit tests for stats_helpers.select_and_rename_columns."""

import pandas as pd
import pytest

from backend.statistics.util import stats_helpers

# normal

def test_select_and_rename_columns_returns_mapped_columns() -> None:
    """select_and_rename_columns returns only present mapped columns with new names."""
    source_df = pd.DataFrame([{"player_name": "Jayden Daniels", "team": "WSH", "ignored": "value"}])
    column_map = {"player_name": "name", "team": "base_team", "season": "base_season"}

    selected = stats_helpers.select_and_rename_columns(source_df, column_map, required_columns=["name", "base_team"], source_name="players")

    assert selected.to_dict("records") == [{"name": "Jayden Daniels", "base_team": "WSH"}]

# edge

def test_select_and_rename_columns_logs_missing_optional_columns(caplog: pytest.LogCaptureFixture) -> None:
    """select_and_rename_columns logs missing optional mapped columns."""
    source_df = pd.DataFrame([{"player_name": "Jayden Daniels"}])
    column_map = {"player_name": "name", "team": "base_team"}

    with caplog.at_level("WARNING"):
        selected = stats_helpers.select_and_rename_columns(source_df, column_map, required_columns=["name"], source_name="players")

    assert selected.to_dict("records") == [{"name": "Jayden Daniels"}]
    assert "players missing optional columns: base_team" in caplog.text

# exception

def test_select_and_rename_columns_raises_for_missing_required_columns() -> None:
    """select_and_rename_columns raises when required mapped columns are missing."""
    source_df = pd.DataFrame([{"player_name": "Jayden Daniels"}])
    column_map = {"player_name": "name", "team": "base_team"}

    with pytest.raises(ValueError, match="players missing required columns: base_team"):
        stats_helpers.select_and_rename_columns(source_df, column_map, required_columns=["name", "base_team"], source_name="players")
