"""
Dynasty format rating adjustments based on player age.
Applies age-based multipliers to account for career longevity and upside potential.
"""

# Age multiplier configuration for dynasty format by position
AGE_MULTIPLIERS = {
    'QB': {'peak_age': 28, 'young_boost': 1.3, 'decline_per_year': 0.05},
    'RB': {'peak_age': 24, 'young_boost': 1.5, 'decline_per_year': 0.15},     # Steepest decline
    'WR': {'peak_age': 26, 'young_boost': 1.4, 'decline_per_year': 0.08},
    'TE': {'peak_age': 27, 'young_boost': 1.3, 'decline_per_year': 0.07},
}


def get_default_age(position: str) -> int:
    """Fallback age when none is available; defaults to position peak age."""
    config = AGE_MULTIPLIERS.get(position)
    return config['peak_age'] if config else 26


def calculate_age_multiplier(age: int, position: str) -> float:
    """
    Calculate age-based multiplier for dynasty format.
    Young players get a boost for upside, older players penalized heavily.
    
    Args:
        age: Player's age
        position: Player's position (QB, RB, WR, TE)
    
    Returns:
        Multiplier to apply to player's rating (0.1 to 1.5)
    """
    if position not in AGE_MULTIPLIERS:
        return 1.0
    
    config = AGE_MULTIPLIERS[position]
    peak_age = config['peak_age']
    young_boost = config['young_boost']
    decline_rate = config['decline_per_year']
    
    # Young players (under peak): boost for upside potential
    if age < peak_age:
        if age < 21:
            return young_boost * 0.9  # Very young, unproven
        # Scale from 1.0 at peak down to lower at age 21
        years_from_peak = peak_age - age
        # Linear from peak (1.0) to young_boost at age 21
        boost_factor = 1.0 + ((young_boost - 1.0) * years_from_peak / (peak_age - 21))
        return min(young_boost, boost_factor)
    
    # At peak age
    elif age == peak_age:
        return 1.0
    
    # Past peak: steep decline
    else:
        years_past_peak = age - peak_age
        multiplier = 1.0 - (years_past_peak * decline_rate)
        return max(0.1, multiplier)  # Floor at 10% to avoid going negative
