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

  it('loads player details and preserves base rating across season changes', async () => {
    getPlayer
      .mockResolvedValueOnce({
        data: {
          name: 'Patrick Mahomes',
          stats: { redraft_rating: 111.1, 'Pass Yds': 4300 },
          available_seasons: [2025, 2024],
          ranking_data: { redraft_rating: 222.2, dynasty_rating: 199.9 },
        },
      })
      .mockResolvedValueOnce({
        data: {
          name: 'Patrick Mahomes',
          stats: { redraft_rating: 999.9, 'Pass Yds': 4000 },
          available_seasons: [2025, 2024],
        },
      });

    const externalRankingData = { redraft_rating: 333.3, dynasty_rating: 250.5 };
    const { result } = renderHook(() => usePlayerDetails());

    await act(async () => {
      await result.current.handlePlayerClick('Patrick Mahomes', externalRankingData);
    });

    expect(getPlayer).toHaveBeenCalledWith('Patrick Mahomes');
    expect(result.current.playerRankingData).toEqual(externalRankingData);
    expect(result.current.currentSeason).toBe(2025);

    await act(async () => {
      await result.current.handleSeasonChange(2024);
    });

    expect(getPlayer).toHaveBeenNthCalledWith(2, 'Patrick Mahomes', 2024);
    expect(result.current.playerDetails.stats.redraft_rating).toBe(333.3);
  });

  it('resets hook state when closing details', async () => {
    getPlayer.mockResolvedValueOnce({
      data: {
        name: 'JaMarr Chase',
        stats: { redraft_rating: 200.1 },
        available_seasons: [2025],
        ranking_data: { redraft_rating: 210.1, dynasty_rating: 250.1 },
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
    expect(result.current.playerRankingData).toBeNull();
  });
});
