
AGE_MULTIPLIERS = {
    'QB': {'peak_age': 28, 'young_boost': 1.3, 'decline_per_year': 0.05},
    'RB': {'peak_age': 24, 'young_boost': 1.15, 'decline_per_year': 0.15},
    'WR': {'peak_age': 26, 'young_boost': 1.4, 'decline_per_year': 0.08},
    'TE': {'peak_age': 27, 'young_boost': 1.3, 'decline_per_year': 0.07},
}

REDRAFT_MULTIPLIERS = {
    'QB': 0.85,   # Lots of good QBs available
    'RB': 1.05,   # Scarce elite talent
    'WR': 1.05,   # Scarce elite talent
    'TE': 1.0,    # Moderate scarcity
}

def get_default_age(position: str) -> int:
    """Fallback age when none is available; defaults to position peak age."""
    config = AGE_MULTIPLIERS.get(position)
    return config['peak_age'] if config else 26


def calculate_age_multiplier(age: int, position: str) -> float:
    if position not in AGE_MULTIPLIERS:
        return 1.0
    
    config = AGE_MULTIPLIERS[position]

    peak_age = config['peak_age']
    young_boost = config['young_boost']
    decline_rate = config['decline_per_year']
    
    if age < peak_age:
        if age < 21:
            return young_boost * 0.9 # Unproven talent adjustment
        years_from_peak = peak_age - age
        boost_factor = 1.0 + ((young_boost - 1.0) * years_from_peak / (peak_age - 21))
        return min(young_boost, boost_factor)
    elif age > peak_age:
        years_past_peak = age - peak_age
        multiplier = 1.0 - (years_past_peak * decline_rate)
        return max(0.1, multiplier)  # Floor at 10% to avoid going negative    
    else:
        return 1.0

def calculate_redraft_multiplier(position: str) -> float:
    return REDRAFT_MULTIPLIERS.get(position, 1.0)
