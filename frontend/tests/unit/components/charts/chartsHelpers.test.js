import { describe, expect, it } from 'vitest';

import {
  buildBarData,
  buildPlayerTrendSeries,
} from '../../../../src/components/charts/chartsHelpers';

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

    expect(buildBarData(players, 'ng_rec_avg_separation', 10)).toEqual([
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

    expect(buildBarData(players, 'pfr_rec_yac_r', 10)).toEqual([
      expect.objectContaining({
        name: 'Qualified Starter',
        value: 6.4,
      }),
    ]);
  });

  it('builds season-by-season trend rows for a selected player', () => {
    const seasonPayloads = [
      {
        season: 2025,
        players: [
          { name: 'Player A', stats: { fp_ppr: 310 } },
          { name: 'Player B', stats: { fp_ppr: 290 } },
        ],
      },
      {
        season: 2024,
        players: [
          { name: 'Player A', stats: { fp_ppr: 275 } },
        ],
      },
    ];

    expect(buildPlayerTrendSeries(seasonPayloads, 'Player A', 'fp_ppr')).toEqual([
      { season: 2024, value: 275 },
      { season: 2025, value: 310 },
    ]);
  });

  it('uses null values when selected player is missing for a season', () => {
    const seasonPayloads = [
      {
        season: 2025,
        players: [{ name: 'Player A', stats: { fp_ppr: 310 } }],
      },
      {
        season: 2024,
        players: [{ name: 'Player B', stats: { fp_ppr: 280 } }],
      },
    ];

    expect(buildPlayerTrendSeries(seasonPayloads, 'Player A', 'fp_ppr')).toEqual([
      { season: 2024, value: null },
      { season: 2025, value: 310 },
    ]);
  });
});
