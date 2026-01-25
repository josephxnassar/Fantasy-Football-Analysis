
POSITIONS = ['QB', 'RB', 'WR', 'TE']

TEAMS = ["ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", 
         "DAL", "DEN", "DET", "GB" , "HOU", "IND", "JAX", "KC" , 
         "LV" , "LAC", "LAR", "MIA", "MIN", "NE" , "NO" , "NYG", 
         "NYJ", "PHI", "PIT", "SF" , "SEA", "TB" , "TEN", "WSH"]

STATISTICS_SEASONS = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

CURRENT_SEASON = 2025

VALID_FORMATS = ["redraft", "dynasty"]

# Stats that should be displayed as whole numbers (counts, yards, TDs)
INTEGER_STATS = {
    'Comp', 'Att', 'Pass Yds', 'Pass TD', 'INT', 'Sacks', 'Sack Yds', 
    'Sack Fum', 'Sack Fum Lost', 'Air Yds', 'YAC', 'Pass 1st', 'Pass 2PT',
    'Carries', 'Rush Yds', 'Rush TD', 'Rush Fum', 'Rush Fum Lost', 'Rush 1st', 'Rush 2PT',
    'Rec', 'Tgt', 'Rec Yds', 'Rec TD', 'Rec Fum', 'Rec Fum Lost', 
    'Rec Air Yds', 'Rec YAC', 'Rec 1st', 'Rec 2PT', 'ST TD',
    'Fantasy Pts', 'PPR Pts'
}

COLUMN_NAME_MAP = {
    # Fantasy Points
    'fantasy_points': 'Fantasy Pts',
    'fantasy_points_ppr': 'PPR Pts',
    
    # Passing Stats
    'completions': 'Comp',
    'attempts': 'Att',
    'passing_yards': 'Pass Yds',
    'passing_tds': 'Pass TD',
    'interceptions': 'INT',
    'sacks': 'Sacks',
    'sack_yards': 'Sack Yds',
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
    'w8dom': 'W8 Dom',
    
    # Keep rating as is
    'rating': 'Rating'
}