"""Application constants and configuration"""

# ========================================================================
# CACHE KEYS - Centralized keys for cache access
# ========================================================================

# Top-level cache names (used by App.caches)
CACHE = {
    "STATISTICS": "Statistics",
    "DEPTH_CHART": "ESPNDepthChart",
    "SCHEDULES": "Schedules",
}

# Statistics cache keys
STATS = {
    "ALL_PLAYERS": "all_players",
    "BY_YEAR": "by_year",
    "PLAYER_WEEKLY_STATS": "player_weekly_stats",
}

# ========================================================================
# POSITIONS & TEAMS
# ========================================================================

# Important fantasy skill positions
POSITIONS = ['QB', 'RB', 'WR', 'TE']

# Team abbreviations
TEAMS = ["ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", 
         "DAL", "DEN", "DET", "GB" , "HOU", "IND", "JAX", "KC" , 
         "LV" , "LAC", "LAR", "MIA", "MIN", "NE" , "NO" , "NYG", 
         "NYJ", "PHI", "PIT", "SF" , "SEA", "TB" , "TEN", "WSH"]

# NFL Division Structure
NFL_DIVISIONS = {
    "AFC": {
        "North": ["BAL", "CIN", "CLE", "PIT"],
        "South": ["HOU", "IND", "JAX", "TEN"],
        "East": ["BUF", "MIA", "NE", "NYJ"],
        "West": ["DEN", "KC", "LV", "LAC"]
    },
    "NFC": {
        "North": ["CHI", "DET", "GB", "MIN"],
        "South": ["ATL", "CAR", "NO", "TB"],
        "East": ["DAL", "NYG", "PHI", "WSH"],
        "West": ["ARI", "LAR", "SF", "SEA"]
    }
}

# Team display names
TEAM_NAMES = {
    "ARI": "Arizona Cardinals", "ATL": "Atlanta Falcons", "BAL": "Baltimore Ravens",
    "BUF": "Buffalo Bills", "CAR": "Carolina Panthers", "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals", "CLE": "Cleveland Browns", "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos", "DET": "Detroit Lions", "GB": "Green Bay Packers",
    "HOU": "Houston Texans", "IND": "Indianapolis Colts", "JAX": "Jacksonville Jaguars",
    "KC": "Kansas City Chiefs", "LAC": "Los Angeles Chargers", "LAR": "Los Angeles Rams",
    "LV": "Las Vegas Raiders", "MIA": "Miami Dolphins", "MIN": "Minnesota Vikings",
    "NE": "New England Patriots", "NO": "New Orleans Saints", "NYG": "New York Giants",
    "NYJ": "New York Jets", "PHI": "Philadelphia Eagles", "PIT": "Pittsburgh Steelers",
    "SF": "San Francisco 49ers", "SEA": "Seattle Seahawks", "TB": "Tampa Bay Buccaneers",
    "TEN": "Tennessee Titans", "WSH": "Washington Commanders"
}

# Available seasons
SEASONS = list(range(2016, 2026))

# Last season in list
CURRENT_SEASON = max(SEASONS)

# Important stats to keep in final output
USEFUL_STATS = [
    'Comp', 'Att', 'Pass Yds', 'Pass TD', 'INT', 'Sacks', 'Sack Yds',
    'Sack Fum', 'Sack Fum Lost', 'Air Yds', 'YAC', 'Pass 1st', 'Pass 2PT',
    'Pass EPA', 'PACR',
    'Carries', 'Rush Yds', 'Yds/Rush', 'Rush TD', 'Rush Fum', 'Rush Fum Lost', 'Rush 1st', 'Rush 2PT', 'Rush EPA',
    'Rec', 'Tgt', 'Rec Yds', 'Yds/Rec', 'Rec TD', 'Rec Fum', 'Rec Fum Lost',
    'Rec Air Yds', 'Rec YAC', 'Rec 1st', 'Rec 2PT', 'Rec EPA', 'RACR',
    'Tgt Share', 'Air Yds Share', 'WOPR', 'ST TD',
    'Non-PPR Pts', 'PPR Pts'
]

# Map raw stat names from API to display names
COLUMN_NAME_MAP = {
    # Fantasy Points
    'fantasy_points': 'Non-PPR Pts',
    'fantasy_points_ppr': 'PPR Pts',

    # Passing Stats
    'completions': 'Comp',
    'attempts': 'Att',
    'passing_yards': 'Pass Yds',
    'passing_tds': 'Pass TD',
    'passing_interceptions': 'INT',
    'sacks_suffered': 'Sacks',
    'sack_yards_lost': 'Sack Yds',
    'sack_fumbles': 'Sack Fum',
    'sack_fumbles_lost': 'Sack Fum Lost',
    'passing_air_yards': 'Air Yds',
    'passing_yards_after_catch': 'YAC',
    'passing_first_downs': 'Pass 1st',
    'passing_epa': 'Pass EPA',
    'passing_2pt_conversions': 'Pass 2PT',
    'pacr': 'PACR',
    'dakota': 'Dakota',

    # Rushing Stats
    'carries': 'Carries',
    'rushing_yards': 'Rush Yds',
    'rushing_tds': 'Rush TD',
    'rushing_fumbles': 'Rush Fum',
    'rushing_fumbles_lost': 'Rush Fum Lost',
    'rushing_first_downs': 'Rush 1st',
    'rushing_epa': 'Rush EPA',
    'rushing_2pt_conversions': 'Rush 2PT',

    # Receiving Stats
    'receptions': 'Rec',
    'targets': 'Tgt',
    'receiving_yards': 'Rec Yds',
    'receiving_tds': 'Rec TD',
    'receiving_fumbles': 'Rec Fum',
    'receiving_fumbles_lost': 'Rec Fum Lost',
    'receiving_air_yards': 'Rec Air Yds',
    'receiving_yards_after_catch': 'Rec YAC',
    'receiving_first_downs': 'Rec 1st',
    'receiving_epa': 'Rec EPA',
    'receiving_2pt_conversions': 'Rec 2PT',
    'racr': 'RACR',
    'target_share': 'Tgt Share',
    'air_yards_share': 'Air Yds Share',
    'wopr': 'WOPR',
    'special_teams_tds': 'ST TD',

    # Market Share Metrics
    'tgt_sh': 'Tgt %',
    'ay_sh': 'Air Yds %',
    'yac_sh': 'YAC %',
    'ry_sh': 'Rec Yds %',
    'rtd_sh': 'Rec TD %',
    'rfd_sh': 'Rec 1st %',
    'rtdfd_sh': 'TD+1st %',
    'ppr_sh': 'PPR %',

    # Advanced Metrics
    'yptmpa': 'Yds/TmAtt',
    'wopr_x': 'WOPR-X',
    'wopr_y': 'WOPR-Y',
    'dom': 'Dominator',
    'w8dom': 'W8 Dom'
}
