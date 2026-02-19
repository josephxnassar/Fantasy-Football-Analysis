/* Stat definitions and categorization for player statistics */

const STAT_DEFINITIONS = {
  'Non-PPR Pts': 'Total fantasy points (standard scoring, non-PPR)',
  'PPR Pts': 'Total fantasy points in PPR (Point Per Reception) format',
  'Snap Share': 'Percent of offensive snaps played',
  
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
  
  'Carries': 'Rushing attempts',
  'Rush Yds': 'Total rushing yards',
  'Rush TD': 'Rushing touchdowns',
  'Rush Fum': 'Rushing fumbles',
  'Rush Fum Lost': 'Rushing fumbles lost',
  'Rush 1st': 'First downs via rushing',
  'Rush EPA': 'Expected Points Added via rushing',
  'Rush 2PT': 'Two-point conversion rushes',
  'Yds/Rush': 'Yards per rushing attempt',

  'Rec': 'Receptions (catches)',
  'Yds/Rec': 'Yards per reception',
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
  
  'Tgt %': 'Target share - percentage of team pass attempts targeted at player',
  'Air Yds %': 'Air yards share - percentage of team total air yards',
  'YAC %': 'Yards after catch share - percentage of team total YAC',
  'Rec Yds %': 'Receiving yards share - share of team receiving yards',
  'Rec TD %': 'Receiving touchdown share - percentage of team receiving TDs',
  'Rec 1st %': 'Receiving first down share - share of team receiving first downs',
  'TD+1st %': 'Combined share of receiving touchdowns and first downs',
  'PPR %': 'PPR fantasy points share - player\'s share of team PPR points',
  
  'RACR': 'Receiver Air Conversion Ratio - ratio of receiving yards to air yards',
  'Yds/TmAtt': 'Yards per team pass attempt - receiving yards divided by team pass attempts',
  'WOPR': 'Weighted Opportunity Rating - combines target and air yards share',
  'WOPR-X': 'Air yards share weight used in WOPR calculation',
  'WOPR-Y': 'Target share weight used in WOPR calculation',
  'Dakota': 'Composite metric of WOPR and YPTMPA - overall efficiency/usage indicator',
  'Dominator': 'Sum of share of receiving yards and touchdowns',
  'W8 Dom': 'Weighted dominator - emphasizes yards more heavily than touchdowns',
  
  'ST TD': 'Special teams touchdowns (returns, etc.)',
};

export function getStatDefinition(statName) {
  return STAT_DEFINITIONS[statName] || 'No definition available';
}

export const POSITION_STAT_GROUPS = {
  'Overall': {
    'Core': ['Non-PPR Pts', 'PPR Pts'],
    'Usage': ['Snap Share'],
    'Passing': ['Pass Yds', 'Pass TD', 'INT'],
    'Rushing': ['Rush Yds', 'Rush TD', 'Carries', 'Yds/Rush'],
    'Receiving': ['Rec', 'Rec Yds', 'Rec TD', 'Tgt', 'Yds/Rec'],
  },
  'QB': {
    'Core': ['Non-PPR Pts', 'PPR Pts'],
    'Usage': ['Snap Share'],
    'Passing': ['Att', 'Comp', 'Pass Yds', 'Pass TD', 'INT', 'Sacks', 'Sack Fum', 'Pass EPA'],
    'Rushing': ['Carries', 'Rush Yds', 'Yds/Rush', 'Rush TD', 'Rush Fum Lost', 'Rush EPA'],
  },
  'RB': {
    'Core': ['Non-PPR Pts', 'PPR Pts'],
    'Usage': ['Snap Share'],
    'Rushing': ['Carries', 'Rush Yds', 'Yds/Rush', 'Rush TD', 'Rush Fum Lost', 'Rush EPA'],
    'Receiving': ['Tgt', 'Rec', 'Rec Yds', 'Yds/Rec', 'Rec TD', 'Rec YAC', 'Rec Fum Lost', 'Rec EPA'],
  },
  'WR': {
    'Core': ['Non-PPR Pts', 'PPR Pts'],
    'Usage': ['Snap Share'],
    'Receiving': ['Tgt', 'Rec', 'Rec Yds', 'Yds/Rec', 'Rec TD', 'Rec YAC', 'Rec Fum Lost', 'Rec EPA'],
    'Rushing': ['Carries', 'Rush Yds', 'Yds/Rush', 'Rush TD', 'Rush Fum Lost', 'Rush EPA'],
  },
  'TE': {
    'Core': ['Non-PPR Pts', 'PPR Pts'],
    'Usage': ['Snap Share'],
    'Receiving': ['Tgt', 'Rec', 'Rec Yds', 'Yds/Rec', 'Rec TD', 'Rec YAC', 'Rec Fum Lost', 'Rec EPA'],
    'Rushing': ['Carries', 'Rush Yds', 'Yds/Rush', 'Rush TD', 'Rush Fum Lost', 'Rush EPA'],
  },
};

const MISSING_STAT_DEFAULTS = {
  'Pass EPA': 0,
  'Rush EPA': 0,
  'Rec EPA': 0,
};

/**
 * Group stats by position and category
 * Works with both aggregated and weekly stats (backend normalizes all stat names to display format)
 * @param {Object} stats - Stats object with display-named fields
 * @param {string} position - Player position (QB, RB, WR, TE)
 * @returns {Object} Stats grouped by category
 */
export function groupStatsByPosition(stats, position) {
  const grouped = {};
  
  // Get stats structure for this position
  const positionGroups = POSITION_STAT_GROUPS[position];
  if (!positionGroups) return grouped;
  
  // Metadata fields to skip
  const skipFields = new Set(['season', 'week']);

  // Build output using configured stat order for deterministic rendering.
  Object.entries(positionGroups).forEach(([category, statList]) => {
    const orderedStats = {};
    statList.forEach((statName) => {
      if (skipFields.has(statName)) return;
      const value = stats[statName];
      if (value != null) {
        orderedStats[statName] = value;
      } else if (Object.prototype.hasOwnProperty.call(MISSING_STAT_DEFAULTS, statName)) {
        orderedStats[statName] = MISSING_STAT_DEFAULTS[statName];
      }
    });
    if (Object.keys(orderedStats).length > 0) {
      grouped[category] = orderedStats;
    }
  });

  return grouped;
}
