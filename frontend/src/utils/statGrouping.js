// Groups and normalizes backend stats using the shared metadata maps.

import { STAT_META } from './statMeta';

export function hasDisplayValue(value) {
  // Shared null/NaN guard used across grouping and formatting helpers.
  return value !== null && value !== undefined && !(typeof value === 'number' && Number.isNaN(value));
}

function isVisibleStatValue(value, options = {}) {
  // Optional hideZero flag removes placeholder zeros from UI cards.
  if (!hasDisplayValue(value)) return false;
  if (options.hideZero && typeof value === 'number' && value === 0) return false;
  return true;
}

export function normalizeStatsRecord(stats) {
  // Keep only known, displayable stat keys from the backend payload.
  const normalized = {};
  if (!stats || typeof stats !== 'object') return normalized;

  Object.entries(stats).forEach(([rawKey, value]) => {
    if (!hasDisplayValue(value)) return;
    const key = rawKey.trim();
    if (!Object.prototype.hasOwnProperty.call(STAT_META, key)) return;
    normalized[key] = value;
  });

  return normalized;
}

export function groupStatsByCategoryMap(stats, categoryMap, options = {}) {
  // Generic grouping helper driven by explicit category -> stat key lists.
  const grouped = {};
  if (!stats || typeof stats !== 'object') return grouped;
  const normalized = normalizeStatsRecord(stats);

  Object.entries(categoryMap).forEach(([category, statKeys]) => {
    const orderedStats = {};
    statKeys.forEach((statKey) => {
      const value = normalized[statKey];
      // Skip seasons where a stat did not exist yet.
      if (statKey === 'pfr_pass_on_tgt_pct' && Number(value) === 0) {
        return;
      }
      if (isVisibleStatValue(value, options)) {
        orderedStats[statKey] = value;
      }
    });
    if (Object.keys(orderedStats).length > 0) {
      grouped[category] = orderedStats;
    }
  });

  return grouped;
}
