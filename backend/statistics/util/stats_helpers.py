"""Helper functions for statistics transformations and cache shaping."""

import logging
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

def _safe_rate(df: pd.DataFrame, numerator: str, denominator: str) -> pd.Series:
    """Compute a rounded per-unit rate while handling divide-by-zero/NaN."""
    return df[numerator].div(df[denominator]).replace([float("inf"), -float("inf")], 0).fillna(0).round(1)

def add_derived_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived stats (Yds/Rec, Yds/Rush) in a non-fragmenting way."""
    source_map = {"Yds/Rec": ("Rec Yds", "Rec"), "Yds/Rush": ("Rush Yds", "Carries")}
    derived = {out_col: _safe_rate(df, num_col, den_col) for out_col, (num_col, den_col) in source_map.items() if {num_col, den_col}.issubset(df.columns)}
    return pd.concat([df, pd.DataFrame(derived, index=df.index)], axis=1) if derived else df

def build_all_players(
    player_positions: Dict[str, str],
    eligible_players: set[str],
    player_ages: Dict[str, int],
    player_headshots: Dict[str, str],
    player_teams: Dict[str, str],
    player_rookies: Dict[str, bool],
) -> List[Dict]:
    """Build pre-assembled player list with player metadata for API consumption."""
    return [
        {
            "name": player_name,
            "position": player_positions.get(player_name),
            "age": player_ages.get(player_name),
            "headshot_url": player_headshots.get(player_name),
            "team": player_teams.get(player_name),
            "is_rookie": player_rookies.get(player_name, False),
            "is_eligible": player_name in eligible_players,
        }
        for player_name in player_positions
    ]
