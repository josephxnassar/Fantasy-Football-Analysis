"""Team color definitions for the Fantasy Football Analysis Tool."""

TEAM_COLORS = {
    'ARI': {'primary': '#97233F', 'secondary': '#000000', 'accent': '#FFB612'},  # Cardinals
    'ATL': {'primary': '#A71930', 'secondary': '#000000', 'accent': '#A5ACAF'},  # Falcons
    'BAL': {'primary': '#241773', 'secondary': '#000000', 'accent': '#9E7C0C'},  # Ravens
    'BUF': {'primary': '#00338D', 'secondary': '#C60C30', 'accent': '#FFFFFF'},  # Bills
    'CAR': {'primary': '#0085CA', 'secondary': '#101820', 'accent': '#BFC0BF'},  # Panthers
    'CHI': {'primary': '#0B162A', 'secondary': '#C83803', 'accent': '#FFFFFF'},  # Bears
    'CIN': {'primary': '#FB4F14', 'secondary': '#000000', 'accent': '#FFFFFF'},  # Bengals
    'CLE': {'primary': '#311D00', 'secondary': '#FF3C00', 'accent': '#FFFFFF'},  # Browns
    'DAL': {'primary': '#003594', 'secondary': '#041E42', 'accent': '#869397'},  # Cowboys
    'DEN': {'primary': '#FB4F14', 'secondary': '#002244', 'accent': '#FFFFFF'},  # Broncos
    'DET': {'primary': '#0076B6', 'secondary': '#B0B7BC', 'accent': '#FFFFFF'},  # Lions
    'GB': {'primary': '#203731', 'secondary': '#FFB612', 'accent': '#FFFFFF'},   # Packers
    'HOU': {'primary': '#03202F', 'secondary': '#A71930', 'accent': '#FFFFFF'},  # Texans
    'IND': {'primary': '#002C5F', 'secondary': '#A2AAAD', 'accent': '#FFFFFF'},  # Colts
    'JAX': {'primary': '#006778', 'secondary': '#D7A22A', 'accent': '#9F792C'},  # Jaguars
    'KC': {'primary': '#E31837', 'secondary': '#FFB81C', 'accent': '#FFFFFF'},   # Chiefs
    'LV': {'primary': '#000000', 'secondary': '#A5ACAF', 'accent': '#FFFFFF'},   # Raiders
    'LAC': {'primary': '#0080C6', 'secondary': '#FFC20E', 'accent': '#FFFFFF'},  # Chargers
    'LAR': {'primary': '#003594', 'secondary': '#FFA300', 'accent': '#FF8200'}, # Rams
    'MIA': {'primary': '#008E97', 'secondary': '#FC4C02', 'accent': '#005778'}, # Dolphins
    'MIN': {'primary': '#4F2683', 'secondary': '#FFC62F', 'accent': '#FFFFFF'},  # Vikings
    'NE': {'primary': '#002244', 'secondary': '#C60C30', 'accent': '#B0B7BC'},  # Patriots
    'NO': {'primary': '#D3BC8D', 'secondary': '#101820', 'accent': '#FFFFFF'},  # Saints
    'NYG': {'primary': '#0B2265', 'secondary': '#A71930', 'accent': '#A5ACAF'}, # Giants
    'NYJ': {'primary': '#125740', 'secondary': '#000000', 'accent': '#FFFFFF'}, # Jets
    'PHI': {'primary': '#004C54', 'secondary': '#A5ACAF', 'accent': '#000000'}, # Eagles
    'PIT': {'primary': '#FFB612', 'secondary': '#101820', 'accent': '#003087'}, # Steelers
    'SF': {'primary': '#AA0000', 'secondary': '#B3995D', 'accent': '#000000'},  # 49ers
    'SEA': {'primary': '#002244', 'secondary': '#69BE28', 'accent': '#A5ACAF'}, # Seahawks
    'TB': {'primary': '#D50A0A', 'secondary': '#34302B', 'accent': '#FF7900'},  # Buccaneers
    'TEN': {'primary': '#0C2340', 'secondary': '#4B92DB', 'accent': '#C8102E'}, # Titans
    'WSH': {'primary': '#5A1414', 'secondary': '#FFB612', 'accent': '#FFFFFF'}, # Commanders
}

def get_team_colors(team_abbr):
    """Get the color scheme for a team.
    
    Args:
        team_abbr (str): Team abbreviation (e.g., 'SF', 'KC')
        
    Returns:
        dict: Dictionary with primary, secondary, and accent colors
    """
    return TEAM_COLORS.get(team_abbr.upper(), {
        'primary': '#343a40',  # Default dark gray
        'secondary': '#6c757d',  # Default gray
        'accent': '#ffffff'  # White
    })
