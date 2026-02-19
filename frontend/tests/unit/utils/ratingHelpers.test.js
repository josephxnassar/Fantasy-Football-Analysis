import { describe, expect, it } from 'vitest';

import { getRatingValue, sortPlayersByRating } from '../../../src/utils/ratingHelpers';

describe('ratingHelpers', () => {
  it('formats selected rating field to two decimals', () => {
    const player = { redraft_rating: 123.4567, dynasty_rating: 99 };

    expect(getRatingValue(player, 'redraft')).toBe('123.46');
    expect(getRatingValue(player, 'dynasty')).toBe('99.00');
  });

  it('returns N/A when selected rating field is missing', () => {
    expect(getRatingValue({ name: 'No Rating' }, 'redraft')).toBe('N/A');
  });

  it('sorts players descending by selected format rating', () => {
    const players = [
      { name: 'A', redraft_rating: 80, dynasty_rating: 70 },
      { name: 'B', redraft_rating: 95, dynasty_rating: 90 },
      { name: 'C', redraft_rating: 85, dynasty_rating: 60 },
    ];

    expect(sortPlayersByRating(players, 'redraft').map((p) => p.name)).toEqual(['B', 'C', 'A']);
    expect(sortPlayersByRating(players, 'dynasty').map((p) => p.name)).toEqual(['B', 'A', 'C']);
  });
});
