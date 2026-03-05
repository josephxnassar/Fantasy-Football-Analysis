import { describe, expect, it } from 'vitest';

import { buildPresetProfile } from '../../../../src/components/rankings/rankingPresets';

describe('rankingPresets', () => {
  const groups = [
    { category: 'Passing Volume', stats: ['pass_att'] },
    { category: 'Passing Efficiency', stats: ['passing_epa'] },
    { category: 'Accuracy & Risk', stats: ['pfr_pass_bad_throw_pct'] },
  ];

  it('builds balanced preset with neutral-positive defaults', () => {
    const profile = buildPresetProfile('balanced', groups);
    expect(profile.statWeights).toEqual({});
    expect(profile.categoryWeights).toEqual({
      'Passing Volume': 1,
      'Passing Efficiency': 1,
      'Accuracy & Risk': 1,
    });
  });

  it('builds volume preset with stronger volume and reduced efficiency/risk', () => {
    const profile = buildPresetProfile('volume', groups);
    expect(profile.categoryWeights).toEqual({
      'Passing Volume': 2,
      'Passing Efficiency': 0,
      'Accuracy & Risk': 0,
    });
  });
});
