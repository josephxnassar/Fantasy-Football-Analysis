"""
Helper functions for API endpoints to reduce code duplication and improve readability.
"""
import logging
from typing import Tuple, Optional, List

logger = logging.getLogger(__name__)


def find_player_in_cache(player_name: str, cache_data: dict) -> Tuple[Optional[dict], Optional[str]]:
    """
    Search for a player across all positions in the cache.
    
    Args:
        player_name: Name of the player to find
        cache_data: Dictionary with position keys and DataFrame values
    
    Returns:
        Tuple of (player_data_dict, position) or (None, None) if not found
    """
    for position, df in cache_data.items():
        if player_name in df.index:
            return df.loc[player_name].to_dict(), position
    return None, None


def get_player_available_seasons(player_name: str, by_year_stats: dict) -> List[int]:
    """
    Get list of seasons where a player has statistical data.
    
    Args:
        player_name: Name of the player
        by_year_stats: Dictionary with season keys and position DataFrames
    
    Returns:
        Sorted list of season years where player appears
    """
    seasons = []
    for season, season_data in by_year_stats.items():
        for position, df in season_data.items():
            if player_name in df.index:
                seasons.append(season)
                break
    return sorted(seasons)


def find_player_team(player_name: str, depth_charts: dict) -> Optional[str]:
    """
    Find which team a player is on by searching depth charts.
    
    Args:
        player_name: Name of the player
        depth_charts: Dictionary with team keys and depth chart DataFrames
    
    Returns:
        Team abbreviation (e.g., 'CIN') or None if not found
    """
    for team, dc_data in depth_charts.items():
        try:
            for col in dc_data.columns:
                if player_name in dc_data[col].values:
                    return team
        except Exception as e:
            logger.warning(f"Error searching depth chart for team {team}: {e}")
            continue
    return None


def filter_stats(stats: dict, integer_stats: set) -> dict:
    """
    Filter and format player statistics.
    
    Removes stats with 0 or near-0 values and converts appropriate stats to integers.
    
    Args:
        stats: Dictionary of stat name to value
        integer_stats: Set of stat names that should be whole numbers
    
    Returns:
        Filtered and formatted stats dictionary
    """
    # Filter out stats with 0 or near-0 values (keep only meaningful stats)
    filtered = {
        stat: value for stat, value in stats.items() 
        if not (isinstance(value, (int, float)) and abs(value) < 0.01)
    }
    
    # Convert appropriate stats to whole numbers
    for stat in filtered:
        if stat in integer_stats and isinstance(filtered[stat], (int, float)):
            filtered[stat] = int(round(filtered[stat]))
    
    return filtered
