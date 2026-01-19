POSITIONS = ['QB', 'RB', 'WR', 'TE']

TEAMS = ["ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", 
         "DAL", "DEN", "DET", "GB" , "HOU", "IND", "JAX", "KC" , 
         "LV" , "LAC", "LAR", "MIA", "MIN", "NE" , "NO" , "NYG", 
         "NYJ", "PHI", "PIT", "SF" , "SEA", "TB" , "TEN", "WSH"]

STATISTICS_SEASONS = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

# Valid fantasy league formats
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