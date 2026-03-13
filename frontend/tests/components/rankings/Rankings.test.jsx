import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import Rankings from '../../../src/components/rankings/Rankings';
import { useChartData } from '../../../src/hooks/useChartData';
import { useSessionStorageObject } from '../../../src/hooks/useSessionStorageObject';

vi.mock('../../../src/hooks/useChartData', () => ({
  useChartData: vi.fn(),
}));

vi.mock('../../../src/hooks/useSessionStorageObject', () => ({
  useSessionStorageObject: vi.fn(),
}));

const CHART_DATA_MOCK = {
  season: 2025,
  available_seasons: [2025, 2024],
  stat_columns: ['fp_ppr_rank'],
  players: [
    {
      name: 'Josh Allen',
      team: 'BUF',
      position: 'QB',
      age: 29,
      stats: { fp_ppr_rank: 1 },
    },
    {
      name: 'Lamar Jackson',
      team: 'BAL',
      position: 'QB',
      age: 28,
      stats: { fp_ppr_rank: 2 },
    },
  ],
};

describe('Rankings', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useChartData.mockReturnValue({
      chartData: CHART_DATA_MOCK,
      loading: false,
      error: null,
    });
    useSessionStorageObject.mockImplementation((_key, defaultValue = {}) => [defaultValue, vi.fn()]);
  });

  it('opens player modal at selected season when season callback is available', async () => {
    const user = userEvent.setup();
    const onPlayerClick = vi.fn();
    const onPlayerSeasonClick = vi.fn();

    render(<Rankings onPlayerClick={onPlayerClick} onPlayerSeasonClick={onPlayerSeasonClick} />);

    await user.click(screen.getByRole('button', { name: 'Josh Allen' }));

    expect(onPlayerSeasonClick).toHaveBeenCalledWith('Josh Allen', 2025);
    expect(onPlayerClick).not.toHaveBeenCalled();
  });

  it('falls back to basic player click when season callback is unavailable', async () => {
    const user = userEvent.setup();
    const onPlayerClick = vi.fn();

    render(<Rankings onPlayerClick={onPlayerClick} />);

    await user.click(screen.getByRole('button', { name: 'Josh Allen' }));

    expect(onPlayerClick).toHaveBeenCalledWith('Josh Allen');
  });
});
