import { describe, expect, it } from 'vitest';

import { buildBarData } from '../../../../src/features/statistics/charts/chartsHelpers';

describe('buildBarData', () => {
  it('filters route-running metrics by minimum target volume', () => {
    const players = [
      {
        name: 'Small Sample',
        position: 'WR',
        team: 'KC',
        stats: {
          ng_rec_avg_separation: 4.2,
          targets: 12,
        },
      },
      {
        name: 'Qualified Receiver',
        position: 'WR',
        team: 'MIN',
        stats: {
          ng_rec_avg_separation: 3.1,
          targets: 96,
        },
      },
    ];

    expect(buildBarData(players, 'ng_rec_avg_separation')).toEqual([
      expect.objectContaining({
        name: 'Qualified Receiver',
        value: 3.1,
      }),
    ]);
  });

  it('filters receiving YAC rates by minimum reception volume', () => {
    const players = [
      {
        name: 'Big Play Specialist',
        position: 'WR',
        team: 'MIA',
        stats: {
          pfr_rec_yac_r: 9.8,
          rec: 14,
        },
      },
      {
        name: 'Qualified Starter',
        position: 'WR',
        team: 'DET',
        stats: {
          pfr_rec_yac_r: 6.4,
          rec: 78,
        },
      },
    ];

    expect(buildBarData(players, 'pfr_rec_yac_r')).toEqual([
      expect.objectContaining({
        name: 'Qualified Starter',
        value: 6.4,
      }),
    ]);
  });

  it('caps leaderboard rows at 50 players by default', () => {
    const players = Array.from({ length: 55 }, (_, index) => ({
      name: `Player ${index + 1}`,
      position: 'RB',
      team: 'DET',
      stats: { fp_ppr: 400 - index },
    }));

    const rows = buildBarData(players, 'fp_ppr');

    expect(rows).toHaveLength(50);
    expect(rows[0].name).toBe('Player 1');
    expect(rows.at(-1)?.name).toBe('Player 50');
  });
});
