import { describe, expect, it } from 'vitest';

import { RANKING_GROUPS } from '../../../../src/features/statistics/rankings/rankingGroups';
import { buildRankings, getRankableGroups } from '../../../../src/features/statistics/rankings/rankingsHelpers';

describe('rankingsHelpers', () => {
  it('filters unavailable stats from rankable groups', () => {
    const groups = getRankableGroups(
      'RB',
      ['fp_ppr', 'rush_yds', 'rush_att_rank'],
      RANKING_GROUPS
    );

    expect(groups).toEqual([
      { category: 'Rushing Production', stats: ['rush_yds'] },
    ]);
  });

  it('ranks players with sample-size thresholds applied', () => {
    const players = [
      {
        name: 'Small Sample',
        position: 'WR',
        age: 26,
        team: 'KC',
        stats: {
          ng_rec_avg_separation: 4.2,
          targets: 12,
        },
      },
      {
        name: 'Qualified A',
        position: 'WR',
        age: 24,
        team: 'MIN',
        stats: {
          ng_rec_avg_separation: 3.4,
          targets: 95,
        },
      },
      {
        name: 'Qualified B',
        position: 'WR',
        age: 25,
        team: 'DET',
        stats: {
          ng_rec_avg_separation: 2.8,
          targets: 105,
        },
      },
    ];

    const rankableGroups = [
      { category: 'Route & Separation', stats: ['ng_rec_avg_separation'] },
    ];

    const ranked = buildRankings(players, rankableGroups, { 'Route & Separation': 2 }, {}, 10);

    expect(ranked.map((row) => row.name)).toEqual(['Qualified A', 'Qualified B']);
    expect(ranked[0].age).toBe(24);
    expect(ranked[0].score).toBeGreaterThan(ranked[1].score);
  });

  it('treats lower-is-better metrics as inverse for scoring', () => {
    const players = [
      {
        name: 'Lower Drop',
        position: 'WR',
        team: 'LAR',
        stats: {
          pfr_rec_drop_pct: 2,
          targets: 90,
        },
      },
      {
        name: 'Higher Drop',
        position: 'WR',
        team: 'BUF',
        stats: {
          pfr_rec_drop_pct: 8,
          targets: 90,
        },
      },
    ];

    const rankableGroups = [{ category: 'Receiving Efficiency', stats: ['pfr_rec_drop_pct'] }];

    const ranked = buildRankings(players, rankableGroups, { 'Receiving Efficiency': 1 }, {}, 10);

    expect(ranked[0].name).toBe('Lower Drop');
    expect(ranked[0].score).toBeGreaterThan(ranked[1].score);
  });

  it('includes touchdown rank category when TD rank stats are available for Overall', () => {
    const groups = getRankableGroups(
      'Overall',
      ['fp_ppr_rank', 'exp_fp_rank', 'pass_td_rank', 'rush_td_rank', 'rec_td_rank'],
      RANKING_GROUPS
    );

    expect(groups).toEqual([
      { category: 'Positional Dominance', stats: ['fp_ppr_rank', 'exp_fp_rank'] },
      { category: 'Touchdown Dominance', stats: ['pass_td_rank', 'rush_td_rank', 'rec_td_rank'] },
    ]);
  });
});
