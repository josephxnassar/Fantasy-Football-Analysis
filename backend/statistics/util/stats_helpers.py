"""Helper functions for statistics transformations, calculations, and multipliers"""

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

def _ranks_from_dict(ratings: Dict[str, float]) -> Dict[str, int]:
    """Convert {player: rating} to {player: rank} (1 = best)."""
    if not ratings:
        return {}
    rank_df = pd.DataFrame(ratings.items(), columns=["player", "rating"])
    rank_df["rank"] = rank_df["rating"].rank(method="min", ascending=False).astype(int)
    return dict(zip(rank_df["player"], rank_df["rank"]))

def calculate_overall_ranks(ratings: Dict[str, float], eligible_players: set) -> Dict[str, int]:
    """Calculate overall ranks for ratings among eligible players."""
    return _ranks_from_dict({player: rating for player, rating in ratings.items() if player in eligible_players})

def calculate_position_ranks(ratings: Dict[str, float], player_positions: Dict[str, str], eligible_players: set) -> Dict[str, int]:
    """Calculate position-level ranks for ratings."""
    # Build {position: {player: rating}} in one pass
    position_groups: Dict[str, Dict[str, float]] = {}
    for player, position in player_positions.items():
        if player in eligible_players and player in ratings:
            position_groups.setdefault(position, {})[player] = ratings[player]
    return {player: rank for pos_ratings in position_groups.values() for player, rank in _ranks_from_dict(pos_ratings).items()}

def build_all_players(redraft_ratings: Dict[str, float], dynasty_ratings: Dict[str, float], player_positions: Dict[str, str], eligible_players: set, player_ages: Dict[str, int], player_headshots: Dict[str, str], player_teams: Dict[str, str], player_rookies: Dict[str, bool], overall_rank_redraft: Dict[str, int], overall_rank_dynasty: Dict[str, int], pos_rank_redraft: Dict[str, int], pos_rank_dynasty: Dict[str, int]) -> List[Dict]:
    """Build pre-assembled player list with all metadata for API consumption"""
    return [{"name": player_name,
             "position": player_positions.get(player_name),
             "age": player_ages.get(player_name),
             "redraft_rating": redraft_ratings[player_name],
             "dynasty_rating": dynasty_ratings.get(player_name),
             "headshot_url": player_headshots.get(player_name),
             "team": player_teams.get(player_name),
             "is_rookie": player_rookies.get(player_name, False),
             "is_eligible": player_name in eligible_players,
             "overall_rank_redraft": overall_rank_redraft.get(player_name),
             "overall_rank_dynasty": overall_rank_dynasty.get(player_name),
             "pos_rank_redraft": pos_rank_redraft.get(player_name),
             "pos_rank_dynasty": pos_rank_dynasty.get(player_name)} for player_name in redraft_ratings]
