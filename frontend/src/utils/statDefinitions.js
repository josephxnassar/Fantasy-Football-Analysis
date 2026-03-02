/* Stat label/format API plus re-exported grouping helpers. */

import { STAT_META } from './statMeta';
import { groupStatsByCategoryMap, hasDisplayValue, normalizeStatsRecord } from './statGrouping';

export { groupStatsByCategoryMap, normalizeStatsRecord };

export function getStatLabel(statName) {
  // Uses canonical metadata first; falls back to raw key if unknown.
  const key = typeof statName === 'string' ? statName.trim() : statName;
  return STAT_META[key]?.label || statName;
}

export function getStatDefinition(statName) {
  const key = typeof statName === 'string' ? statName.trim() : statName;
  return STAT_META[key]?.description || '';
}

export function formatStatForDisplay(statName, value) {
  if (!hasDisplayValue(value)) return value;
  if (typeof value !== 'number') return value;

  // Format type is driven by metadata so tabs stay consistent.
  const key = typeof statName === 'string' ? statName.trim() : statName;
  const format = STAT_META[key]?.format;
  if (format === 'int') return Math.round(value);
  if (format === 'decimal1') return value.toFixed(1);
  if (format === 'decimal2') return value.toFixed(2);
  if (format === 'percent1') return `${value.toFixed(1)}%`;
  return Number.isInteger(value) ? value : value.toFixed(2);
}
