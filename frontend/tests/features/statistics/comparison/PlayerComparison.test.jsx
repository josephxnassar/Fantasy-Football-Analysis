import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import PlayerComparison from '../../../../src/features/statistics/comparison/PlayerComparison';
import { usePlayerComparisonState } from '../../../../src/features/statistics/comparison/usePlayerComparisonState';

vi.mock('../../../../src/features/statistics/comparison/usePlayerComparisonState', () => ({
  usePlayerComparisonState: vi.fn(),
}));

describe('PlayerComparison', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    usePlayerComparisonState.mockReturnValue({
      comparisonSlots: [
        {
          id: 1,
          playerName: 'Josh Allen',
          team: 'BUF',
          position: 'QB',
          season: 2024,
          availableSeasons: [2024],
          loading: false,
          error: null,
        },
      ],
      selectionError: null,
      playerOptionsLoading: false,
      playerOptionsError: null,
      playerOptions: ['Josh Allen'],
      selectedPlayers: [{ id: 1, playerName: 'Josh Allen', season: 2024 }],
      comparisonProfileLabel: 'QB',
      comparisonRows: [],
      statWinnersByKey: {},
      weeksWinners: new Set(),
      winCountsBySlot: {},
      handlePlayerSelect: vi.fn(),
      handleSeasonChange: vi.fn(),
      handleRemovePlayer: vi.fn(),
    });
  });

  it('renders the comparison header and slot controls from comparison state', () => {
    render(<PlayerComparison />);

    expect(screen.getByText('Detected Profile')).toBeInTheDocument();
    expect(screen.getByText('QB')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Player Slots' })).toBeInTheDocument();
    expect(screen.getByLabelText('Player')).toHaveValue('Josh Allen');
    expect(screen.getByLabelText('Season')).toHaveValue('2024');
  });
});
