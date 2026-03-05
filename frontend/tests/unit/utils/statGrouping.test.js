import { describe, expect, it } from 'vitest';

import { groupStatsByCategoryMap } from '../../../src/utils/statGrouping';
import { PRODUCTION_GROUPS } from '../../../src/utils/statMeta';

describe('groupStatsByCategoryMap', () => {
  it('groups QB stats into correct categories', () => {
    const stats = {
      fp_ppr: 312.4,
      pass_att: 520,
      pass_yds: 4102,
      pass_td: 31,
      passing_epa: 0.15,
      rush_att: 22,
      rush_yds: 121,
    };

    const grouped = groupStatsByCategoryMap(stats, PRODUCTION_GROUPS.QB);

    expect(grouped.Fantasy).toHaveProperty('fp_ppr', 312.4);
    expect(grouped.Passing).toHaveProperty('pass_att', 520);
    expect(grouped.Passing).toHaveProperty('pass_yds', 4102);
    expect(grouped['Passing Efficiency']).toHaveProperty('passing_epa', 0.15);
    expect(grouped.Rushing).toHaveProperty('rush_att', 22);
  });

  it('groups WR stats with receiving and usage categories', () => {
    const stats = {
      fp_ppr: 280.0,
      targets: 151,
      rec: 109,
      rec_yds: 1462,
      rec_td: 11,
      target_share: 0.28,
      wopr: 0.55,
    };

    const grouped = groupStatsByCategoryMap(stats, PRODUCTION_GROUPS.WR);

    expect(grouped.Receiving).toHaveProperty('targets', 151);
    expect(grouped.Receiving).toHaveProperty('rec_yds', 1462);
    expect(grouped.Usage).toHaveProperty('target_share', 0.28);
    expect(grouped.Usage).toHaveProperty('wopr', 0.55);
  });

  it('groups RB receiving broken tackles when data exists', () => {
    const stats = {
      targets: 62,
      rec: 49,
      rec_yds: 388,
      receiving_yards_after_catch: 271,
      pfr_rec_brk_tkl: 8,
    };

    const grouped = groupStatsByCategoryMap(stats, PRODUCTION_GROUPS.RB);

    expect(grouped.Receiving).toHaveProperty('targets', 62);
    expect(grouped.Receiving).toHaveProperty('receiving_yards_after_catch', 271);
    expect(grouped.Receiving).toHaveProperty('pfr_rec_brk_tkl', 8);
  });

  it('excludes categories where no stats have data', () => {
    const stats = { fp_ppr: 200.0 };
    const grouped = groupStatsByCategoryMap(stats, PRODUCTION_GROUPS.RB);

    expect(grouped.Fantasy).toHaveProperty('fp_ppr', 200.0);
    expect(grouped.Rushing).toBeUndefined();
    expect(grouped.Receiving).toBeUndefined();
  });

  it('drops unknown stat keys not in STAT_META', () => {
    const stats = { fp_ppr: 100.0, totally_fake_stat: 999 };
    const grouped = groupStatsByCategoryMap(stats, PRODUCTION_GROUPS.QB);

    expect(grouped.Fantasy).toHaveProperty('fp_ppr', 100.0);
    const allValues = Object.values(grouped).flatMap((cat) => Object.keys(cat));
    expect(allValues).not.toContain('totally_fake_stat');
  });

  it('returns empty object for null stats input', () => {
    const grouped = groupStatsByCategoryMap(null, PRODUCTION_GROUPS.QB);
    expect(grouped).toEqual({});
  });

  it('hides zero values when hideZero option is set', () => {
    const stats = { fp_ppr: 0, pass_att: 520 };
    const grouped = groupStatsByCategoryMap(stats, PRODUCTION_GROUPS.QB, { hideZero: true });

    expect(grouped.Fantasy).toBeUndefined();
    expect(grouped.Passing).toHaveProperty('pass_att', 520);
  });
});
