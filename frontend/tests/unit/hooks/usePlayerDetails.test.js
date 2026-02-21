import { act, renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { usePlayerDetails } from '../../../src/hooks/usePlayerDetails';
import { getPlayer } from '../../../src/api';

vi.mock('../../../src/api', () => ({
  getPlayer: vi.fn(),
}));

describe('usePlayerDetails', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads player details across season changes', async () => {
    getPlayer
      .mockResolvedValueOnce({
        data: {
          name: 'Patrick Mahomes',
          stats: { 'Pass Yds': 4300 },
          available_seasons: [2025, 2024],
        },
      })
      .mockResolvedValueOnce({
        data: {
          name: 'Patrick Mahomes',
          stats: { 'Pass Yds': 4000 },
          available_seasons: [2025, 2024],
        },
      });

    const { result } = renderHook(() => usePlayerDetails());

    await act(async () => {
      await result.current.handlePlayerClick('Patrick Mahomes');
    });

    expect(getPlayer).toHaveBeenCalledWith('Patrick Mahomes');
    expect(result.current.currentSeason).toBe(2025);

    await act(async () => {
      await result.current.handleSeasonChange(2024);
    });

    expect(getPlayer).toHaveBeenNthCalledWith(2, 'Patrick Mahomes', 2024);
    expect(result.current.playerDetails.stats['Pass Yds']).toBe(4000);
  });

  it('resets hook state when closing details', async () => {
    getPlayer.mockResolvedValueOnce({
      data: {
        name: 'JaMarr Chase',
        stats: { 'Rec Yds': 1716 },
        available_seasons: [2025],
      },
    });

    const { result } = renderHook(() => usePlayerDetails());

    await act(async () => {
      await result.current.handlePlayerClick('JaMarr Chase');
    });

    await act(async () => {
      result.current.closeDetails();
    });

    expect(result.current.playerDetails).toBeNull();
    expect(result.current.currentSeason).toBeNull();
    expect(result.current.availableSeasons).toEqual([]);
  });
});
