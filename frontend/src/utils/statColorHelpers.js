/* Stat color-coding helpers - returns CSS class from stat thresholds. */

const STAT_THRESHOLDS = {
  fp_ppr: 20,
  fp_std: 15,
  exp_fp: 15,
  volume_score: 65,

  pass_att: 35,
  attempts: 35,
  completions: 24,
  pass_yds: 300,
  passing_yards: 275,
  pass_td: 3,
  passing_tds: 2,

  rush_att: 20,
  carries: 18,
  rush_yds: 100,
  rushing_yards: 85,
  rush_td: 1,
  rushing_tds: 1,

  rec: 8,
  receptions: 6,
  targets: 10,
  rec_yds: 100,
  receiving_yards: 85,
  rec_td: 1,
  receiving_tds: 1,

  passing_first_downs: 15,
  rushing_first_downs: 5,
  receiving_first_downs: 5,
  sc_offense_snaps: 35,
  sc_offense_pct: 60,
  target_share: 20,
  air_yards_share: 20,
  wopr: 0.6,

  ydsrec: 12,
  ydsrush: 5,

  ng_pass_passer_rating: 95,
  ng_pass_cmp_pct: 65,
  ng_rec_catch_pct: 70,
  ng_rec_avg_separation: 3,
  ng_rush_avg_rush_yds: 4.5,
  ng_rush_rush_yds_over_exp_per_att: 0.5,

  pfr_rush_ybc_att: 2.5,
  pfr_rush_yac_att: 1.8,
  pfr_rec_ybc_r: 5,
  pfr_rec_yac_r: 4,

  // Backward-compatible legacy labels
  pprpts: 20,
  nonpprpts: 15,
  att: 35,
  passyds: 300,
  passtd: 3,
  rushyds: 100,
  rushtd: 1,
  tgt: 10,
  recyds: 100,
  rectd: 1,
};

const LOWER_IS_BETTER_TOKENS = [
  'interception',
  '_int',
  'fumble',
  'drop',
  'bad_throw',
  'times_sacked',
  'times_pressured',
  'pressure_pct',
];

function toKey(statName) {
  // Normalize stat key for consistent lookup logic.
  return String(statName || '').trim().toLowerCase();
}

function compactKey(statName) {
  // Removes punctuation for fallback threshold matches.
  return toKey(statName).replace(/[^a-z0-9]/g, '');
}

function isLowerBetter(statName) {
  // Detect turnover/error-style stats where lower values are better.
  const key = toKey(statName);
  return LOWER_IS_BETTER_TOKENS.some((token) => key.includes(token));
}

function isPercentMetric(statName) {
  // Percent/rate stats use percent-specific color thresholds.
  const key = toKey(statName);
  return key.endsWith('_pct') || key.includes('percentile');
}

function normalizePercentageValue(statName, value) {
  // Convert ratio-form percentages (0-1) into 0-100 for threshold comparisons.
  if (!Number.isFinite(value)) return value;
  const key = toKey(statName);
  const isRatioPercent = key.endsWith('_pct') || key.includes('percent') || key.includes('share');
  if (isRatioPercent && Math.abs(value) <= 1) {
    return value * 100;
  }
  return value;
}

function getThreshold(statName) {
  // Tries exact key first, then compact key fallback.
  const key = toKey(statName);
  const compact = compactKey(statName);
  return STAT_THRESHOLDS[key] ?? STAT_THRESHOLDS[compact];
}

/**
 * Get color class for a stat value.
 * @param {string} statName - Stat key.
 * @param {number} value - Stat value.
 * @returns {string} CSS class.
 */
export function getStatColorClass(statName, value) {
  if (value === null || value === undefined || Number.isNaN(value)) return '';
  const numeric = typeof value === 'number' ? value : Number(value);
  if (!Number.isFinite(numeric)) return '';

  const normalizedValue = normalizePercentageValue(statName, numeric);

  if (isLowerBetter(statName)) {
    if (isPercentMetric(statName)) {
      if (normalizedValue <= 10) return 'stat-good';
      if (normalizedValue <= 20) return 'stat-medium';
      return 'stat-poor';
    }
    if (normalizedValue === 0) return 'stat-good';
    if (normalizedValue <= 1) return 'stat-medium';
    return 'stat-poor';
  }

  const threshold = getThreshold(statName);
  if (threshold !== undefined) {
    if (normalizedValue >= threshold) return 'stat-good';
    if (normalizedValue >= threshold * 0.5) return 'stat-medium';
    return 'stat-poor';
  }

  if (isPercentMetric(statName)) {
    if (normalizedValue >= 80) return 'stat-good';
    if (normalizedValue >= 60) return 'stat-medium';
    return 'stat-poor';
  }

  const key = toKey(statName);
  if (key.includes('td')) {
    if (numeric >= 2) return 'stat-good';
    if (numeric >= 1) return 'stat-medium';
    return 'stat-poor';
  }
  if (key.includes('yds') || key.includes('yards')) {
    if (numeric >= 100) return 'stat-good';
    if (numeric >= 50) return 'stat-medium';
    return 'stat-poor';
  }
  if (key.includes('att') || key.includes('attempt')) {
    if (numeric >= 20) return 'stat-good';
    if (numeric >= 10) return 'stat-medium';
    return 'stat-poor';
  }

  // Generic fallback so numeric stats are always color-scored.
  if (normalizedValue < 0) return 'stat-poor';
  if (normalizedValue === 0) return 'stat-poor';
  if (Math.abs(normalizedValue) < 1) return 'stat-medium';
  if (Math.abs(normalizedValue) < 5) return 'stat-medium';
  return 'stat-good';
}
