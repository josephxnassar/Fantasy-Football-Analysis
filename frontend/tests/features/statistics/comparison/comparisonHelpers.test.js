import { describe, expect, it } from 'vitest';

import {
  buildComparisonRows,
  buildComparisonWins,
  getWinningSlotIdsForStat,
  getWinningSlotIdsForWeeks,
} from '../../../../src/features/statistics/comparison/comparisonHelpers';
import { PRODUCTION_GROUPS_NO_RANKS } from '../../../../src/shared/utils/statMeta';

describe('buildComparisonRows', () => {
  it('builds category and stat rows in profile order', () => {
    const rows = buildComparisonRows('Overall');
    const expectedStatCount = Object.values(PRODUCTION_GROUPS_NO_RANKS.Overall).reduce(
      (total, stats) => total + stats.length,
      0
    );

    expect(rows[0]).toEqual({
      type: 'category',
      id: 'category:Fantasy',
      label: 'Fantasy',
    });
    expect(rows[1]).toEqual({
      type: 'stat',
      id: `stat:${PRODUCTION_GROUPS_NO_RANKS.Overall.Fantasy[0]}`,
      statKey: PRODUCTION_GROUPS_NO_RANKS.Overall.Fantasy[0],
      category: 'Fantasy',
    });
    expect(rows.filter((row) => row.type === 'stat')).toHaveLength(expectedStatCount);
  });

  it('falls back to Overall profile rows for unknown profile keys', () => {
    expect(buildComparisonRows('UnknownProfile')).toEqual(buildComparisonRows('Overall'));
  });

  it('includes profile-specific categories and stats for WR', () => {
    const rows = buildComparisonRows('WR');

    expect(rows).toContainEqual({
      type: 'category',
      id: 'category:Receiving Efficiency',
      label: 'Receiving Efficiency',
    });
    expect(rows).toContainEqual({
      type: 'stat',
      id: 'stat:racr',
      statKey: 'racr',
      category: 'Receiving Efficiency',
    });
  });

  it('marks max value as winner for higher-is-better stats', () => {
    const slots = [
      { id: 1, stats: { fp_ppr: 210.3 } },
      { id: 2, stats: { fp_ppr: 225.7 } },
      { id: 3, stats: { fp_ppr: 218.1 } },
    ];

    expect(getWinningSlotIdsForStat('fp_ppr', slots)).toEqual(new Set([2]));
  });

  it('marks min value as winner for lower-is-better stats', () => {
    const slots = [
      { id: 1, stats: { passing_interceptions: 12 } },
      { id: 2, stats: { passing_interceptions: 8 } },
      { id: 3, stats: { passing_interceptions: 10 } },
    ];

    expect(getWinningSlotIdsForStat('passing_interceptions', slots)).toEqual(new Set([2]));
  });

  it('marks lower time-to-throw as winner', () => {
    const slots = [
      { id: 1, stats: { ng_pass_avg_time_to_throw: 2.82 } },
      { id: 2, stats: { ng_pass_avg_time_to_throw: 2.44 } },
      { id: 3, stats: { ng_pass_avg_time_to_throw: 2.67 } },
    ];

    expect(getWinningSlotIdsForStat('ng_pass_avg_time_to_throw', slots)).toEqual(new Set([2]));
  });

  it('marks all tied players as winners on complete ties', () => {
    const slots = [
      { id: 1, stats: { fp_ppr: 200 } },
      { id: 2, stats: { fp_ppr: 200 } },
    ];

    expect(getWinningSlotIdsForStat('fp_ppr', slots)).toEqual(new Set([1, 2]));
  });

  it('picks highest weeks played as winner and tallies wins', () => {
    const slots = [
      { id: 1, weeksPlayed: 17, stats: { fp_ppr: 320, passing_interceptions: 12 } },
      { id: 2, weeksPlayed: 15, stats: { fp_ppr: 310, passing_interceptions: 8 } },
      { id: 3, weeksPlayed: 14, stats: { fp_ppr: 290, passing_interceptions: 11 } },
    ];
    const rows = [
      { type: 'stat', statKey: 'fp_ppr' },
      { type: 'stat', statKey: 'passing_interceptions' },
    ];

    expect(getWinningSlotIdsForWeeks(slots)).toEqual(new Set([1]));
    expect(buildComparisonWins(rows, slots)).toEqual({
      1: 2,
      2: 1,
      3: 0,
    });
  });
});
