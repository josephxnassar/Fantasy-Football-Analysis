/* Canonical stat metadata, labels, and grouping for modal/chart rendering. */

const STAT_META = {
  fp_ppr: {
    label: 'PPR Pts',
    description: 'PPR fantasy points.',
    format: 'decimal1',
  },
  fp_std: {
    label: 'Non-PPR Pts',
    description: 'Standard (non-PPR) fantasy points.',
    format: 'decimal1',
  },
  exp_fp: {
    label: 'Expected Pts',
    description: 'Expected fantasy points from opportunity model.',
    format: 'decimal1',
  },
  volume_score: {
    label: 'Volume Score',
    description: 'Blend of usage percentiles (pass/rush/target volume).',
    format: 'decimal1',
  },

  pass_att: { label: 'Pass Att', description: 'Passing attempts.', format: 'int' },
  pass_yds: { label: 'Pass Yds', description: 'Passing yards.', format: 'int' },
  pass_td: { label: 'Pass TD', description: 'Passing touchdowns.', format: 'int' },

  rush_att: { label: 'Carries', description: 'Rushing attempts.', format: 'int' },
  rush_yds: { label: 'Rush Yds', description: 'Rushing yards.', format: 'int' },
  rush_td: { label: 'Rush TD', description: 'Rushing touchdowns.', format: 'int' },

  rec: { label: 'Rec', description: 'Receptions.', format: 'int' },
  targets: { label: 'Tgt', description: 'Targets.', format: 'int' },
  rec_yds: { label: 'Rec Yds', description: 'Receiving yards.', format: 'int' },
  rec_td: { label: 'Rec TD', description: 'Receiving touchdowns.', format: 'int' },

  fp_ppr_pct: {
    label: 'PPR %ile',
    description: 'Percentile rank in PPR points vs same position context.',
    format: 'percent1',
  },
  pass_att_pct: {
    label: 'Pass Att %ile',
    description: 'Percentile rank in passing volume.',
    format: 'percent1',
  },
  pass_yds_pct: {
    label: 'Pass Yds %ile',
    description: 'Percentile rank in passing yards.',
    format: 'percent1',
  },
  rush_att_pct: {
    label: 'Rush Att %ile',
    description: 'Percentile rank in rushing volume.',
    format: 'percent1',
  },
  rush_yds_pct: {
    label: 'Rush Yds %ile',
    description: 'Percentile rank in rushing yards.',
    format: 'percent1',
  },
  rec_yds_pct: {
    label: 'Rec Yds %ile',
    description: 'Percentile rank in receiving yards.',
    format: 'percent1',
  },
  targets_pct: {
    label: 'Tgt %ile',
    description: 'Percentile rank in targets.',
    format: 'percent1',
  },
  exp_fp_pct: {
    label: 'Expected Pts %ile',
    description: 'Percentile rank in expected points.',
    format: 'percent1',
  },

  'Yds/Rec': {
    label: 'Yds/Rec',
    description: 'Yards per reception.',
    format: 'decimal1',
  },
  'Yds/Rush': {
    label: 'Yds/Rush',
    description: 'Yards per rush attempt.',
    format: 'decimal1',
  },
};

export const POSITION_STAT_GROUPS = {
  Overall: {
    Core: ['fp_ppr', 'fp_ppr_pct', 'fp_std', 'volume_score'],
    Usage: ['pass_att', 'rush_att', 'targets', 'pass_att_pct', 'rush_att_pct', 'targets_pct'],
    Production: ['pass_yds', 'pass_td', 'rush_yds', 'rush_td', 'rec_yds', 'rec_td'],
    Efficiency: ['Yds/Rec', 'Yds/Rush'],
    Opportunity: ['exp_fp', 'exp_fp_pct'],
  },
  QB: {
    Core: ['fp_ppr', 'fp_ppr_pct', 'fp_std', 'volume_score'],
    Passing: ['pass_att', 'pass_yds', 'pass_td', 'pass_att_pct', 'pass_yds_pct'],
    Rushing: ['rush_att', 'rush_yds', 'rush_td', 'rush_att_pct', 'rush_yds_pct', 'Yds/Rush'],
    Opportunity: ['exp_fp', 'exp_fp_pct'],
  },
  RB: {
    Core: ['fp_ppr', 'fp_ppr_pct', 'fp_std', 'volume_score'],
    Rushing: ['rush_att', 'rush_yds', 'rush_td', 'rush_att_pct', 'rush_yds_pct', 'Yds/Rush'],
    Receiving: ['targets', 'rec', 'rec_yds', 'rec_td', 'targets_pct', 'rec_yds_pct', 'Yds/Rec'],
    Opportunity: ['exp_fp', 'exp_fp_pct'],
  },
  WR: {
    Core: ['fp_ppr', 'fp_ppr_pct', 'fp_std', 'volume_score'],
    Receiving: ['targets', 'rec', 'rec_yds', 'rec_td', 'targets_pct', 'rec_yds_pct', 'Yds/Rec'],
    Rushing: ['rush_att', 'rush_yds', 'rush_td', 'Yds/Rush'],
    Opportunity: ['exp_fp', 'exp_fp_pct'],
  },
  TE: {
    Core: ['fp_ppr', 'fp_ppr_pct', 'fp_std', 'volume_score'],
    Receiving: ['targets', 'rec', 'rec_yds', 'rec_td', 'targets_pct', 'rec_yds_pct', 'Yds/Rec'],
    Opportunity: ['exp_fp', 'exp_fp_pct'],
  },
};

function normalizeStatKey(statName) {
  return statName;
}

function hasDisplayValue(value) {
  return value !== null && value !== undefined && !(typeof value === 'number' && Number.isNaN(value));
}

export function getStatLabel(statName) {
  const canonical = normalizeStatKey(statName);
  return STAT_META[canonical]?.label || statName;
}

export function getStatDefinition(statName) {
  const canonical = normalizeStatKey(statName);
  return STAT_META[canonical]?.description || 'No definition available';
}

export function formatStatForDisplay(statName, value) {
  if (!hasDisplayValue(value)) return value;
  if (typeof value !== 'number') return value;

  const canonical = normalizeStatKey(statName);
  const format = STAT_META[canonical]?.format;
  if (format === 'int') return Math.round(value);
  if (format === 'decimal1') return value.toFixed(1);
  if (format === 'percent1') return `${value.toFixed(1)}%`;
  return Number.isInteger(value) ? value : value.toFixed(2);
}

export function normalizeStatsRecord(stats) {
  const normalized = {};
  if (!stats || typeof stats !== 'object') return normalized;

  Object.entries(stats).forEach(([rawKey, value]) => {
    if (!hasDisplayValue(value)) return;
    const canonical = normalizeStatKey(rawKey);
    if (!Object.prototype.hasOwnProperty.call(STAT_META, canonical)) return;
    if (!Object.prototype.hasOwnProperty.call(normalized, canonical) || rawKey === canonical) {
      normalized[canonical] = value;
    }
  });

  return normalized;
}

/**
 * Group stats by position and category, with canonical stat keys.
 * @param {Object} stats - Stats record from API.
 * @param {string} position - Player position.
 * @returns {Object<string, Object<string, number>>} Grouped category map.
 */
export function groupStatsByPosition(stats, position) {
  const grouped = {};
  const positionGroups = POSITION_STAT_GROUPS[position] || POSITION_STAT_GROUPS.Overall;
  const normalized = normalizeStatsRecord(stats);

  Object.entries(positionGroups).forEach(([category, statKeys]) => {
    const orderedStats = {};
    statKeys.forEach((statKey) => {
      const value = normalized[statKey];
      if (hasDisplayValue(value)) {
        orderedStats[statKey] = value;
      }
    });
    if (Object.keys(orderedStats).length > 0) {
      grouped[category] = orderedStats;
    }
  });

  return grouped;
}
