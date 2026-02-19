import { describe, expect, it } from 'vitest';

import { getStatDefinition, groupStatsByPosition } from '../../../src/utils/statDefinitions';

describe('statDefinitions', () => {
  it('groups stats by configured QB categories and keeps missing defaults', () => {
    const grouped = groupStatsByPosition(
      {
        'PPR Pts': 312.4,
        'Non-PPR Pts': 260.2,
        'Snap Share': 0.95,
        Att: 520,
        Comp: 340,
      },
      'QB'
    );

    expect(grouped.Core['PPR Pts']).toBe(312.4);
    expect(grouped.Usage['Snap Share']).toBe(0.95);
    expect(grouped.Passing.Att).toBe(520);
    expect(grouped.Passing.Comp).toBe(340);
    expect(grouped.Passing['Pass EPA']).toBe(0);
  });

  it('returns fallback definition for unknown stats', () => {
    expect(getStatDefinition('does_not_exist')).toBe('No definition available');
  });

  it('does not expose a removed redraft_rating display definition', () => {
    expect(getStatDefinition('redraft_rating')).toBe('No definition available');
  });
});
