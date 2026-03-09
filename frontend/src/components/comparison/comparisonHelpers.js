/* Helpers for ordering direct-comparison rows from production stat metadata. */

import { PRODUCTION_GROUPS_NO_RANKS } from '../../utils/statMeta';
import { isLowerBetterStat } from '../../utils/statDirection';

export function buildComparisonRows(positionProfile = 'Overall') {
  const profileGroups = PRODUCTION_GROUPS_NO_RANKS[positionProfile] || PRODUCTION_GROUPS_NO_RANKS.Overall;
  const rows = [];

  Object.entries(profileGroups).forEach(([category, statKeys]) => {
    rows.push({ type: 'category', id: `category:${category}`, label: category });

    statKeys.forEach((statKey) => {
      rows.push({ type: 'stat', id: `stat:${statKey}`, statKey, category });
    });
  });

  return rows;
}

function toFiniteNumber(value) {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function getWinningSlotIdsFromEntries(entries, lowerIsBetter) {
  if (entries.length < 2) return new Set();

  const values = entries.map((entry) => entry.value);
  const allEqual = values.every((value) => value === values[0]);
  if (allEqual) return new Set(entries.map((entry) => entry.id));

  const targetValue = lowerIsBetter
    ? Math.min(...values)
    : Math.max(...values);

  return new Set(entries.filter((entry) => entry.value === targetValue).map((entry) => entry.id));
}

export function getWinningSlotIdsForStat(statKey, selectedSlots) {
  const numericEntries = selectedSlots
    .map((slot) => ({ id: slot.id, value: toFiniteNumber(slot?.stats?.[statKey]) }))
    .filter((entry) => entry.value !== null);

  return getWinningSlotIdsFromEntries(numericEntries, isLowerBetterStat(statKey));
}

export function getWinningSlotIdsForWeeks(selectedSlots) {
  const numericEntries = selectedSlots
    .map((slot) => ({ id: slot.id, value: toFiniteNumber(slot?.weeksPlayed) }))
    .filter((entry) => entry.value !== null);

  return getWinningSlotIdsFromEntries(numericEntries, false);
}

export function buildComparisonWins(rows, selectedSlots) {
  const wins = Object.fromEntries(selectedSlots.map((slot) => [slot.id, 0]));

  rows.forEach((row) => {
    if (row.type !== 'stat') return;
    const winners = getWinningSlotIdsForStat(row.statKey, selectedSlots);
    winners.forEach((slotId) => {
      wins[slotId] = (wins[slotId] || 0) + 1;
    });
  });

  const weeksWinners = getWinningSlotIdsForWeeks(selectedSlots);
  weeksWinners.forEach((slotId) => {
    wins[slotId] = (wins[slotId] || 0) + 1;
  });

  return wins;
}
