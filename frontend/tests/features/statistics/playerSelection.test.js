import { describe, expect, it, vi } from 'vitest';

import { openPlayerSelection } from '../../../src/features/statistics/playerSelection';

describe('openPlayerSelection', () => {
  it('opens the season-specific player view when the season is valid', () => {
    const onPlayerClick = vi.fn();
    const onPlayerSeasonClick = vi.fn();

    openPlayerSelection({
      playerName: 'DJ Moore',
      season: '2025',
      onPlayerClick,
      onPlayerSeasonClick,
    });

    expect(onPlayerSeasonClick).toHaveBeenCalledWith('DJ Moore', 2025);
    expect(onPlayerClick).not.toHaveBeenCalled();
  });

  it('falls back to the generic player open action when no valid season exists', () => {
    const onPlayerClick = vi.fn();
    const onPlayerSeasonClick = vi.fn();

    openPlayerSelection({
      playerName: 'DJ Moore',
      season: null,
      onPlayerClick,
      onPlayerSeasonClick,
    });

    expect(onPlayerClick).toHaveBeenCalledWith('DJ Moore');
    expect(onPlayerSeasonClick).not.toHaveBeenCalled();
  });
});
