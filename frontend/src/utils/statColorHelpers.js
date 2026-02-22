/* Stat color-coding helpers - returns CSS class from stat thresholds. */

const STAT_THRESHOLDS = {
  fp_ppr: 20,
  fp_std: 15,
  volume_score: 65,

  pass_att: 35,
  pass_yds: 300,
  pass_td: 3,

  rush_att: 20,
  rush_yds: 100,
  rush_td: 1,

  rec: 8,
  targets: 10,
  rec_yds: 100,
  rec_td: 1,

  exp_fp: 15,
  'Yds/Rec': 12,
  'Yds/Rush': 5,

  // Backward-compatible legacy labels
  'PPR Pts': 20,
  'Non-PPR Pts': 15,
  Att: 35,
  'Pass Yds': 300,
  'Pass TD': 3,
  Carries: 20,
  'Rush Yds': 100,
  'Rush TD': 1,
  Rec: 8,
  Tgt: 10,
  'Rec Yds': 100,
  'Rec TD': 1,
};

const LOWER_IS_BETTER = new Set([
  'pass_int',
  'passing_interceptions',
  'INT',
  'interceptions',
  'Sacks',
  'Sack Fum',
  'Rush Fum',
  'Rush Fum Lost',
  'Rec Fum',
  'Rec Fum Lost',
]);

/**
 * Get color class for a stat value.
 * @param {string} statName - Stat key.
 * @param {number} value - Stat value.
 * @returns {string} CSS class.
 */
export function getStatColorClass(statName, value) {
  if (value === null || value === undefined || Number.isNaN(value)) return '';

  if (LOWER_IS_BETTER.has(statName)) {
    if (value === 0) return 'stat-good';
    if (value === 1) return 'stat-medium';
    if (value >= 2) return 'stat-poor';
    return '';
  }

  if (statName.endsWith('_pct')) {
    if (value >= 80) return 'stat-good';
    if (value >= 60) return 'stat-medium';
    return 'stat-poor';
  }

  const threshold = STAT_THRESHOLDS[statName];
  if (!threshold) return '';

  if (value >= threshold) return 'stat-good';
  if (value >= threshold * 0.5) return 'stat-medium';
  return 'stat-poor';
}
