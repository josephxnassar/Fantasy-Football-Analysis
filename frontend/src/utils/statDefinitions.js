/* Stat label/format API plus re-exported grouping helpers. */

import { POSITION_STAT_GROUPS, STAT_META } from './statMeta';
import { groupStatsByCategoryMap, groupStatsByPosition, normalizeStatsRecord } from './statGrouping';

export { groupStatsByCategoryMap, groupStatsByPosition, normalizeStatsRecord, POSITION_STAT_GROUPS };

function hasDisplayValue(value) {
  return value !== null && value !== undefined && !(typeof value === 'number' && Number.isNaN(value));
}

export function getStatLabel(statName) {
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

  const key = typeof statName === 'string' ? statName.trim() : statName;
  const format = STAT_META[key]?.format;
  if (format === 'int') return Math.round(value);
  if (format === 'decimal1') return value.toFixed(1);
  if (format === 'decimal2') return value.toFixed(2);
  if (format === 'percent1') return `${value.toFixed(1)}%`;
  return Number.isInteger(value) ? value : value.toFixed(2);
}
