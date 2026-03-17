// Stat color helpers that map values to CSS classes.

import { isLowerBetterStat } from './statDirection';

const STAT_THRESHOLDS = {
  fp_ppr: 20,
  fp_std: 15,
  exp_fp: 15,

  pass_att: 35,
  completions: 24,
  pass_yds: 300,
  pass_td: 3,

  rush_att: 20,
  rush_yds: 100,
  rush_td: 1,

  rec: 8,
  targets: 10,
  rec_yds: 100,
  rec_td: 1,

  target_share: 20,
  air_yards_share: 20,
  wopr: 0.6,
  sc_offense_pct: 70,

  receiving_yards_after_catch: 40,

  fp_ppr_rank: 10,
  pass_att_rank: 10,
  pass_yds_rank: 10,
  pass_td_rank: 10,
  rush_att_rank: 10,
  rush_yds_rank: 10,
  rush_td_rank: 10,
  targets_rank: 10,
  rec_yds_rank: 10,
  rec_td_rank: 10,
  exp_fp_rank: 10,

  ng_pass_passer_rating: 95,
  ng_rec_catch_pct: 70,
  ng_rec_avg_separation: 3,
  ng_rec_avg_yac: 5,
  ng_rush_rush_yds_over_exp_per_att: 0.5,

  pfr_rush_yac_att: 1.8,
  pfr_rush_yac: 40,
  pfr_rush_ybc_att: 2,
  pfr_rec_yac_r: 4,
  pfr_rec_yac: 300,
  pfr_rec_adot: 10,
  pfr_pass_on_tgt_pct: 78,
};

function toKey(statName) {
  // Normalize stat key for consistent lookup logic.
  return String(statName || '')
    .trim()
    .toLowerCase();
}

function compactKey(statName) {
  // Removes punctuation for fallback threshold matches.
  return toKey(statName).replace(/[^a-z0-9]/g, '');
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

function isRankMetric(statName) {
  return toKey(statName).endsWith('_rank');
}

export function getStatColorClass(statName, value) {
  if (value === null || value === undefined || Number.isNaN(value)) return '';
  const numeric = typeof value === 'number' ? value : Number(value);
  if (!Number.isFinite(numeric)) return '';
  if (isRankMetric(statName) && numeric === 0) return 'stat-no-data';

  const normalizedValue = normalizePercentageValue(statName, numeric);

  if (isLowerBetterStat(statName)) {
    const lowerThreshold = getThreshold(statName);
    if (lowerThreshold !== undefined) {
      if (normalizedValue <= lowerThreshold) return 'stat-good';
      if (normalizedValue <= lowerThreshold * 2) return 'stat-medium';
      return 'stat-poor';
    }
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
