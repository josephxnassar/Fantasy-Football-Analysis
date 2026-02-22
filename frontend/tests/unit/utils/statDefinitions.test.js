import { describe, expect, it } from 'vitest';

import {
  formatStatForDisplay,
  getStatDefinition,
  getStatLabel,
  groupStatsByPosition,
  normalizeStatsRecord,
} from '../../../src/utils/statDefinitions';

describe('statDefinitions', () => {
  it('keeps canonical keys and drops unknown keys', () => {
    const normalized = normalizeStatsRecord({
      fp_ppr: 312.4,
      pass_att: 520,
      pass_yds: 4102,
      pass_td: 31,
      rush_att: 22,
      rush_yds: 121,
      unknown_metric: 999,
    });

    expect(normalized.fp_ppr).toBe(312.4);
    expect(normalized.pass_att).toBe(520);
    expect(normalized.pass_yds).toBe(4102);
    expect(normalized.pass_td).toBe(31);
    expect(normalized.rush_att).toBe(22);
    expect(normalized.rush_yds).toBe(121);
    expect(normalized.unknown_metric).toBeUndefined();
  });

  it('groups canonical stats by configured QB categories', () => {
    const grouped = groupStatsByPosition(
      {
        fp_ppr: 312.4,
        pass_att: 520,
        pass_yds: 4102,
        pass_td: 31,
        rush_att: 22,
        rush_yds: 121,
      },
      'QB'
    );

    expect(grouped.Core.fp_ppr).toBe(312.4);
    expect(grouped.Core.fp_ppr_pct).toBeUndefined();
    expect(grouped.Passing.pass_att).toBe(520);
    expect(grouped.Passing.pass_yds).toBe(4102);
    expect(grouped.Rushing.rush_yds).toBe(121);
  });

  it('formats stat values based on stat meta format', () => {
    expect(formatStatForDisplay('pass_att', 32.8)).toBe(33);
    expect(formatStatForDisplay('fp_ppr', 21.44)).toBe('21.4');
    expect(formatStatForDisplay('fp_ppr_pct', 91.26)).toBe('91.3%');
  });

  it('returns fallback definition for unknown stats', () => {
    expect(getStatDefinition('does_not_exist')).toBe('No definition available');
  });

  it('returns friendly labels for canonical keys', () => {
    expect(getStatLabel('pass_yds')).toBe('Pass Yds');
    expect(getStatLabel('targets_pct')).toBe('Tgt %ile');
  });

  it('does not expose a removed redraft_rating display definition', () => {
    expect(getStatDefinition('redraft_rating')).toBe('No definition available');
  });
});
