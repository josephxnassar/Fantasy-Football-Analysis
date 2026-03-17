import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import PlayerComparisonTable from '../../../../src/features/statistics/comparison/PlayerComparisonTable';

function renderTable(overrides = {}) {
  const props = {
    selectedPlayers: [
      {
        id: 1,
        playerName: 'Josh Allen',
        season: 2024,
        weeksPlayed: 17,
        loading: false,
        stats: {},
      },
    ],
    comparisonRows: [],
    statWinnersByKey: {},
    weeksWinners: new Set(),
    winCountsBySlot: {},
    onPlayerClick: undefined,
    onPlayerSeasonClick: undefined,
    ...overrides,
  };
  return render(<PlayerComparisonTable {...props} />);
}

describe('PlayerComparisonTable', () => {
  it('opens player modal at selected season when season callback is available', async () => {
    const user = userEvent.setup();
    const onPlayerSeasonClick = vi.fn();
    renderTable({ onPlayerSeasonClick });

    await user.click(screen.getByRole('button', { name: 'Josh Allen' }));

    expect(onPlayerSeasonClick).toHaveBeenCalledWith('Josh Allen', 2024);
  });

  it('falls back to player click when season callback is not provided', async () => {
    const user = userEvent.setup();
    const onPlayerClick = vi.fn();
    renderTable({ onPlayerClick });

    await user.click(screen.getByRole('button', { name: 'Josh Allen' }));

    expect(onPlayerClick).toHaveBeenCalledWith('Josh Allen');
  });
});
