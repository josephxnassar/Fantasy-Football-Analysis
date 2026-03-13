import { act, renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { usePlayerDetails } from '../../../src/components/player-details/usePlayerDetails';
import { getPlayer } from '../../../src/api';

vi.mock('../../../src/api', () => ({
  getPlayer: vi.fn(),
}));

describe('usePlayerDetails', () => {
  beforeEach(() => {
    vi.resetAllMocks();
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

    expect(getPlayer).toHaveBeenCalledWith('Patrick Mahomes', null);
    expect(result.current.currentSeason).toBe(2025);

    await act(async () => {
      await result.current.handleSeasonChange(2024);
    });

    expect(getPlayer).toHaveBeenNthCalledWith(2, 'Patrick Mahomes', 2024);
    expect(result.current.playerDetails.stats['Pass Yds']).toBe(4000);
    expect(result.current.detailsError).toBeNull();
  });

  it('opens a player directly at a selected season', async () => {
    getPlayer.mockResolvedValueOnce({
      data: {
        name: 'Patrick Mahomes',
        stats: { 'Pass Yds': 4000 },
        available_seasons: [2025, 2024],
      },
    });

    const { result } = renderHook(() => usePlayerDetails());

    await act(async () => {
      await result.current.handlePlayerSeasonClick('Patrick Mahomes', 2024);
    });

    expect(getPlayer).toHaveBeenCalledWith('Patrick Mahomes', 2024);
    expect(result.current.currentSeason).toBe(2024);
    expect(result.current.playerDetails.stats['Pass Yds']).toBe(4000);
    expect(result.current.detailsError).toBeNull();
  });

  it('keeps the current season data when a season change fails', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    getPlayer
      .mockResolvedValueOnce({
        data: {
          name: 'Patrick Mahomes',
          stats: { 'Pass Yds': 4300 },
          available_seasons: [2025, 2024],
        },
      })
      .mockRejectedValueOnce(new Error('Season request failed'));

    const { result } = renderHook(() => usePlayerDetails());

    await act(async () => {
      await result.current.handlePlayerClick('Patrick Mahomes');
    });

    await act(async () => {
      await result.current.handleSeasonChange(2024);
    });

    expect(result.current.currentSeason).toBe(2025);
    expect(result.current.playerDetails.stats['Pass Yds']).toBe(4300);
    expect(result.current.detailsError).toBe('Failed to load 2024 season data.');
  });

  it('exposes an error and clears stale state when the initial player load fails', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    getPlayer.mockRejectedValueOnce(new Error('Player request failed'));

    const { result } = renderHook(() => usePlayerDetails());

    await act(async () => {
      await result.current.handlePlayerClick('Patrick Mahomes');
    });

    expect(result.current.loadingDetails).toBe(false);
    expect(result.current.playerDetails).toBeNull();
    expect(result.current.currentSeason).toBeNull();
    expect(result.current.availableSeasons).toEqual([]);
    expect(result.current.detailsError).toBe('Failed to load player details.');
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
    expect(result.current.detailsError).toBeNull();
  });
});
