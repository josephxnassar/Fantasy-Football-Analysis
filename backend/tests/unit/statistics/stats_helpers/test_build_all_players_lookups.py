"""Unit tests for stats_helpers.build_all_players_lookups."""

import pandas as pd
import pytest

from backend.statistics.util import stats_helpers

# normal

def test_build_all_players_lookups_builds_expected_lookup_data() -> None:
    """build_all_players_lookups builds positions, ages, eligibility, headshots, teams, and rookies."""
    rosters_df = pd.DataFrame([
        {"base_player_display_name": "Jayden Daniels", "base_player_id": "1", "base_pos": "QB", "base_birth_date": "2000-12-18", "base_headshot_url": "old-headshot", "base_season": 2024, "base_status": "ACT", "base_team": "WSH", "base_entry_year": 2024},
        {"base_player_display_name": "Jayden Daniels", "base_player_id": "1", "base_pos": "QB", "base_birth_date": "2000-12-18", "base_headshot_url": "new-headshot", "base_season": 2025, "base_status": "ACT", "base_team": "WSH", "base_entry_year": 2024},
        {"base_player_display_name": "Cam Ward", "base_player_id": "2", "base_pos": "QB", "base_birth_date": "2002-05-25", "base_headshot_url": "cam-headshot", "base_season": 2025, "base_status": "ACT", "base_team": "TEN", "base_entry_year": 2025},
        {"base_player_display_name": "Retired Player", "base_player_id": "3", "base_pos": "WR", "base_birth_date": "1990-01-01", "base_headshot_url": "retired-headshot", "base_season": 2025, "base_status": "RET", "base_team": "ARI", "base_entry_year": 2012},
    ])
    player_key = ("Jayden Daniels", "1")
    cam_key = ("Cam Ward", "2")
    retired_key = ("Retired Player", "3")
    today = pd.Timestamp.now().normalize()
    expected_age = (today - pd.Timestamp("2000-12-18")).days // 365

    player_positions, player_ages, eligible_players, player_headshots, player_teams, rookie_players = stats_helpers.build_all_players_lookups(rosters_df, 2025)

    assert player_positions == {player_key: "QB", cam_key: "QB", retired_key: "WR"}
    assert player_ages[player_key] == expected_age
    assert player_headshots[player_key] == "new-headshot"
    assert player_teams == {player_key: "WSH", cam_key: "TEN", retired_key: "ARI"}
    assert eligible_players == {player_key, cam_key}
    assert rookie_players == {cam_key}

# edge

def test_build_all_players_lookups_ignores_invalid_rows_and_blank_current_team() -> None:
    """build_all_players_lookups ignores rows with missing keys and omits blank current teams."""
    rosters_df = pd.DataFrame([
        {"base_player_display_name": "Jayden Daniels", "base_player_id": "1", "base_pos": "QB", "base_birth_date": "invalid-date", "base_headshot_url": "", "base_season": 2025, "base_status": "ACT", "base_team": "", "base_entry_year": 2024},
        {"base_player_display_name": None, "base_player_id": "2", "base_pos": "RB", "base_birth_date": "2001-01-01", "base_headshot_url": "headshot", "base_season": 2025, "base_status": "ACT", "base_team": "BUF", "base_entry_year": 2025},
    ])
    player_key = ("Jayden Daniels", "1")

    player_positions, player_ages, eligible_players, player_headshots, player_teams, rookie_players = stats_helpers.build_all_players_lookups(rosters_df, 2025)

    assert player_positions == {player_key: "QB"}
    assert player_ages == {}
    assert eligible_players == {player_key}
    assert player_headshots == {}
    assert player_teams == {}
    assert rookie_players == set()

# exception

def test_build_all_players_lookups_raises_for_missing_required_column() -> None:
    """build_all_players_lookups raises when a required roster column is missing."""
    rosters_df = pd.DataFrame([
        {"base_player_display_name": "Jayden Daniels", "base_pos": "QB", "base_birth_date": "2000-12-18", "base_headshot_url": "headshot", "base_season": 2025, "base_status": "ACT", "base_team": "WSH", "base_entry_year": 2024},
    ])

    with pytest.raises(KeyError):
        stats_helpers.build_all_players_lookups(rosters_df, 2025)
