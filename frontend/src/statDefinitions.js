// Stat definitions for tooltips
export const STAT_DEFINITIONS = {
  // Fantasy Points
  'Fantasy Pts': 'Total fantasy points (standard scoring)',
  'PPR Pts': 'Total fantasy points in PPR (Point Per Reception) format',
  'Rating': 'Overall player rating calculated by machine learning model',
  
  // Passing Stats
  'Comp': 'Pass completions',
  'Att': 'Pass attempts',
  'Pass Yds': 'Total passing yards',
  'Pass TD': 'Passing touchdowns',
  'INT': 'Interceptions thrown',
  'Sacks': 'Times sacked',
  'Sack Yds': 'Yards lost due to sacks',
  'Sack Fum': 'Fumbles on sacks',
  'Sack Fum Lost': 'Fumbles lost on sacks',
  'Air Yds': 'Total air yards (distance ball travels in air)',
  'YAC': 'Yards after catch (total for QB\'s completions)',
  'Pass 1st': 'First downs via passing',
  'Pass EPA': 'Expected Points Added via passing',
  'Pass 2PT': 'Two-point conversion passes',
  'PACR': 'Passing Air Conversion Ratio',
  
  // Rushing Stats
  'Carries': 'Rushing attempts',
  'Rush Yds': 'Total rushing yards',
  'Rush TD': 'Rushing touchdowns',
  'Rush Fum': 'Rushing fumbles',
  'Rush Fum Lost': 'Rushing fumbles lost',
  'Rush 1st': 'First downs via rushing',
  'Rush EPA': 'Expected Points Added via rushing',
  'Rush 2PT': 'Two-point conversion rushes',
  
  // Receiving Stats
  'Rec': 'Receptions (catches)',
  'Tgt': 'Targets (passes thrown to player)',
  'Rec Yds': 'Receiving yards',
  'Rec TD': 'Receiving touchdowns',
  'Rec Fum': 'Receiving fumbles',
  'Rec Fum Lost': 'Receiving fumbles lost',
  'Rec Air Yds': 'Air yards on receptions',
  'Rec YAC': 'Yards after catch',
  'Rec 1st': 'First downs via receiving',
  'Rec EPA': 'Expected Points Added via receiving',
  'Rec 2PT': 'Two-point conversion receptions',
  
  // Market Share Metrics
  'Tgt %': 'Target share - percentage of team pass attempts targeted at player',
  'Air Yds %': 'Air yards share - percentage of team total air yards',
  'YAC %': 'Yards after catch share - percentage of team total YAC',
  'Rec Yds %': 'Receiving yards share - share of team receiving yards',
  'Rec TD %': 'Receiving touchdown share - percentage of team receiving TDs',
  'Rec 1st %': 'Receiving first down share - share of team receiving first downs',
  'TD+1st %': 'Combined share of receiving touchdowns and first downs',
  'PPR %': 'PPR fantasy points share - player\'s share of team PPR points',
  
  // Advanced Metrics
  'RACR': 'Receiver Air Conversion Ratio - ratio of receiving yards to air yards',
  'Yds/TmAtt': 'Yards per team pass attempt - receiving yards divided by team pass attempts',
  'WOPR': 'Weighted Opportunity Rating - combines target and air yards share',
  'WOPR-X': 'Air yards share weight used in WOPR calculation',
  'WOPR-Y': 'Target share weight used in WOPR calculation',
  'Dakota': 'Composite metric of WOPR and YPTMPA - overall efficiency/usage indicator',
  'Dominator': 'Sum of share of receiving yards and touchdowns',
  'W8 Dom': 'Weighted dominator - emphasizes yards more heavily than touchdowns',
  
  // Special Teams
  'ST TD': 'Special teams touchdowns (returns, etc.)',
};

export function getStatDefinition(statName) {
  return STAT_DEFINITIONS[statName] || 'No definition available';
}

// Key stats to highlight for each position
export const KEY_STATS_BY_POSITION = {
  'QB': ['Pass Yds', 'Pass TD', 'INT', 'Comp', 'Att', 'PPR Pts', 'Rating'],
  'RB': ['Rush Yds', 'Rush TD', 'Carries', 'Rec', 'Rec Yds', 'PPR Pts', 'Rating'],
  'WR': ['Rec', 'Rec Yds', 'Rec TD', 'Tgt', 'Rec YAC', 'PPR Pts', 'Rating'],
  'TE': ['Rec', 'Rec Yds', 'Rec TD', 'Tgt', 'Rec YAC', 'PPR Pts', 'Rating'],
};

export function isKeyStat(statName, position) {
  const keyStats = KEY_STATS_BY_POSITION[position] || [];
  return keyStats.includes(statName);
}

// Stat categories for grouping
export const STAT_CATEGORIES = {
  'Core': ['Fantasy Pts', 'PPR Pts', 'Rating'],
  'Passing': ['Comp', 'Att', 'Pass Yds', 'Pass TD', 'INT', 'Sacks', 'Sack Yds', 'Air Yds', 'YAC', 'Pass 1st', 'Pass EPA', 'Pass 2PT', 'PACR'],
  'Rushing': ['Carries', 'Rush Yds', 'Rush TD', 'Rush Fum', 'Rush Fum Lost', 'Rush 1st', 'Rush EPA', 'Rush 2PT'],
  'Receiving': ['Rec', 'Tgt', 'Rec Yds', 'Rec TD', 'Rec Fum', 'Rec Fum Lost', 'Rec Air Yds', 'Rec YAC', 'Rec 1st', 'Rec EPA', 'Rec 2PT'],
  'Market Share': ['Tgt %', 'Air Yds %', 'YAC %', 'Rec Yds %', 'Rec TD %', 'Rec 1st %', 'TD+1st %', 'PPR %'],
  'Advanced': ['RACR', 'Yds/TmAtt', 'WOPR', 'WOPR-X', 'WOPR-Y', 'Dakota', 'Dominator', 'W8 Dom', 'ST TD'],
};

export function groupStatsByCategory(stats) {
  const grouped = {};
  
  // Initialize all categories
  Object.keys(STAT_CATEGORIES).forEach(category => {
    grouped[category] = {};
  });
  
  // Group stats into categories
  Object.entries(stats).forEach(([statName, value]) => {
    let placed = false;
    for (const [category, statList] of Object.entries(STAT_CATEGORIES)) {
      if (statList.includes(statName)) {
        grouped[category][statName] = value;
        placed = true;
        break;
      }
    }
    // If stat doesn't fit any category, put in Advanced
    if (!placed) {
      grouped['Advanced'][statName] = value;
    }
  });
  
  // Remove empty categories
  Object.keys(grouped).forEach(category => {
    if (Object.keys(grouped[category]).length === 0) {
      delete grouped[category];
    }
  });
  
  return grouped;
}
