/**
 * File overview: Comparison-specific grouping and winner-calculation helpers for the player comparison feature.
 */

import { getProductionGroupsWithoutRankings } from '../../../shared/utils/statMeta';
import { isLowerBetterStat } from '../../../shared/utils/statDirection';

// Mixed-position comparisons use one explicit cross-position surface instead of
// trying to blend per-position production groups at runtime.
const COMPARISON_GROUPS = {
  QB: getProductionGroupsWithoutRankings('QB'),
  RB: getProductionGroupsWithoutRankings('RB'),
  WR: getProductionGroupsWithoutRankings('WR'),
  TE: getProductionGroupsWithoutRankings('TE'),
  CrossPosition: {
    Fantasy: ['fp_ppr', 'fp_std', 'exp_fp'],
    Volume: ['pass_att', 'rush_att', 'targets', 'sc_offense_pct'],
    Yardage: ['pass_yds', 'rush_yds', 'rec_yds'],
    Touchdowns: ['pass_td', 'rush_td', 'rec_td'],
    Efficiency: ['passing_epa', 'rushing_epa', 'receiving_epa'],
  },
};

export function buildComparisonRows(positionProfile = 'CrossPosition') {
  const profileGroups = COMPARISON_GROUPS[positionProfile] || COMPARISON_GROUPS.CrossPosition;
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

  // Treat ties as shared wins so the table can highlight equal leaders instead of
  // arbitrarily picking one player.
  const values = entries.map((entry) => entry.value);
  const allEqual = values.every((value) => value === values[0]);
  if (allEqual) return new Set(entries.map((entry) => entry.id));

  const targetValue = lowerIsBetter ? Math.min(...values) : Math.max(...values);

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
