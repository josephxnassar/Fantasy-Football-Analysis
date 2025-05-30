"""Team information and utilities for the Fantasy Football Analysis Tool."""

TEAM_FULLNAMES = {
    'ARI': 'Arizona Cardinals',
    'ATL': 'Atlanta Falcons',
    'BAL': 'Baltimore Ravens',
    'BUF': 'Buffalo Bills',
    'CAR': 'Carolina Panthers',
    'CHI': 'Chicago Bears',
    'CIN': 'Cincinnati Bengals',
    'CLE': 'Cleveland Browns',
    'DAL': 'Dallas Cowboys',
    'DEN': 'Denver Broncos',
    'DET': 'Detroit Lions',
    'GB': 'Green Bay Packers',
    'HOU': 'Houston Texans',
    'IND': 'Indianapolis Colts',
    'JAX': 'Jacksonville Jaguars',
    'KC': 'Kansas City Chiefs',
    'LV': 'Las Vegas Raiders',
    'LAC': 'Los Angeles Chargers',
    'LAR': 'Los Angeles Rams',
    'MIA': 'Miami Dolphins',
    'MIN': 'Minnesota Vikings',
    'NE': 'New England Patriots',
    'NO': 'New Orleans Saints',
    'NYG': 'New York Giants',
    'NYJ': 'New York Jets',
    'PHI': 'Philadelphia Eagles',
    'PIT': 'Pittsburgh Steelers',
    'SF': 'San Francisco 49ers',
    'SEA': 'Seattle Seahawks',
    'TB': 'Tampa Bay Buccaneers',
    'TEN': 'Tennessee Titans',
    'WSH': 'Washington Commanders'
}

def get_team_fullname(team_abbr):
    """Get the full team name from abbreviation.
    
    Args:
        team_abbr (str): Team abbreviation (e.g., 'SF', 'KC')
        
    Returns:
        str: Full team name or the input if not found
    """
    return TEAM_FULLNAMES.get(team_abbr, team_abbr)

def get_team_logo_path(team_abbr):
    """Get the path to the team's logo.
    
    Args:
        team_abbr (str): Team abbreviation (e.g., 'SF', 'KC')
        
    Returns:
        str: Path to the team's logo SVG file
    """
    return f"static/images/teams/{team_abbr}.svg"
