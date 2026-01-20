"""
Helper functions for API endpoints to reduce code duplication and improve readability.
"""
import logging
from typing import Tuple, Optional, List, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)


def calculate_enriched_rankings(stats_cache: dict, position_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Calculate enriched player rankings with both redraft and dynasty ratings plus percentiles.
    This function is shared by both rankings and search endpoints.
    
    Args:
        stats_cache: Statistics cache from app.caches['Statistics']
        position_filter: Optional position to filter by (QB, RB, WR, TE)
    
    Returns:
        List of player dictionaries with all ratings and percentiles
    """
    from backend.util.position_multipliers import calculate_age_multiplier, calculate_redraft_multiplier, get_default_age
    from backend.util import constants
    
    averaged_stats = stats_cache.get('averaged', stats_cache)
    player_ages = stats_cache.get('player_ages', {})
    
    all_players = []
    
    for pos in constants.POSITIONS:
        if position_filter and pos != position_filter:
            continue
        if pos not in averaged_stats:
            continue
            
        df = averaged_stats[pos].copy()
        
        if 'Rating' not in df.columns or df.empty:
            continue
        
        # Vectorized dynasty rating calculation
        player_ages_list = [player_ages.get(name, get_default_age(pos)) for name in df.index]
        multipliers = [calculate_age_multiplier(age, pos) for age in player_ages_list]
        redraft_multiplier = calculate_redraft_multiplier(pos)
        
        df['DynastyRating'] = df['Rating'] * multipliers
        df['Rating'] = df['Rating'] * redraft_multiplier
        df['Age'] = player_ages_list
        
        # Position percentiles
        df['pos_percentile_redraft'] = df['Rating'].rank(pct=True) * 100
        df['pos_percentile_dynasty'] = df['DynastyRating'].rank(pct=True) * 100
        
        # Convert to records for this position
        index_name = df.index.name if df.index.name else 'index'
        records = df.reset_index().rename(columns={index_name: 'name'}).to_dict('records')
        all_players.extend([{**rec, 'position': pos} for rec in records])
    
    # Overall percentiles across all positions
    if all_players:
        overall_df = pd.DataFrame(all_players)
        overall_df['overall_percentile_redraft'] = overall_df['Rating'].rank(pct=True) * 100
        overall_df['overall_percentile_dynasty'] = overall_df['DynastyRating'].rank(pct=True) * 100
        
        # Map back to player records
        for idx, row in overall_df.iterrows():
            all_players[idx]['overall_percentile_redraft'] = row['overall_percentile_redraft']
            all_players[idx]['overall_percentile_dynasty'] = row['overall_percentile_dynasty']
    
    return all_players


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
