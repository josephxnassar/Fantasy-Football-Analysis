import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { deferred } from '../../setup';
import { getPlayerTrendData } from '../../../src/api';
import {
  __resetSeasonChartDataCache,
  useSeasonChartData,
} from '../../../src/hooks/useSeasonChartData';

vi.mock('../../../src/api', () => ({
  getPlayerTrendData: vi.fn(),
}));

describe('useSeasonChartData', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    __resetSeasonChartDataCache();
  });

  it('loads season trend payload for player + stat', async () => {
    getPlayerTrendData.mockResolvedValueOnce({
      data: {
        player_name: 'Patrick Mahomes',
        points: [{ season: 2025, value: 4280 }],
      },
    });

    const { result } = renderHook(() => useSeasonChartData('QB', 'Patrick Mahomes', 'Pass Yds', true));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(getPlayerTrendData).toHaveBeenCalledWith('Patrick Mahomes', 'QB', 'Pass Yds');
    expect(result.current.data?.points).toEqual([{ season: 2025, value: 4280 }]);
    expect(result.current.error).toBeNull();
  });

  it('skips fetch when disabled or query params are missing', async () => {
    const disabled = renderHook(() => useSeasonChartData('QB', 'Patrick Mahomes', 'Pass Yds', false));
    const missingPlayer = renderHook(() => useSeasonChartData('QB', '', 'Pass Yds', true));
    const missingStat = renderHook(() => useSeasonChartData('QB', 'Patrick Mahomes', '', true));

    await waitFor(() => {
      expect(disabled.result.current.loading).toBe(false);
      expect(missingPlayer.result.current.loading).toBe(false);
      expect(missingStat.result.current.loading).toBe(false);
    });

    expect(getPlayerTrendData).not.toHaveBeenCalled();
  });

  it('ignores stale responses when player changes mid-request', async () => {
    const firstRequest = deferred();
    const secondRequest = deferred();
    getPlayerTrendData
      .mockImplementationOnce(() => firstRequest.promise)
      .mockImplementationOnce(() => secondRequest.promise);

    const { result, rerender } = renderHook(
      ({ playerName }) => useSeasonChartData('QB', playerName, 'Pass Yds', true),
      { initialProps: { playerName: 'Patrick Mahomes' } }
    );

    rerender({ playerName: 'Joe Burrow' });

    await waitFor(() => {
      expect(getPlayerTrendData).toHaveBeenCalledTimes(2);
    });

    await act(async () => {
      firstRequest.resolve({ data: { points: [{ season: 2025, value: 4280 }] } });
      await Promise.resolve();
    });

    expect(result.current.data).toBeNull();

    await act(async () => {
      secondRequest.resolve({ data: { points: [{ season: 2025, value: 4650 }] } });
      await Promise.resolve();
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data?.points).toEqual([{ season: 2025, value: 4650 }]);
  });

  it('reuses cached payload for identical query key', async () => {
    getPlayerTrendData.mockResolvedValueOnce({
      data: { points: [{ season: 2025, value: 4280 }] },
    });

    const first = renderHook(() => useSeasonChartData('QB', 'Patrick Mahomes', 'Pass Yds', true));
    await waitFor(() => {
      expect(first.result.current.loading).toBe(false);
    });
    first.unmount();

    const second = renderHook(() => useSeasonChartData('QB', 'Patrick Mahomes', 'Pass Yds', true));
    await waitFor(() => {
      expect(second.result.current.loading).toBe(false);
    });

    expect(getPlayerTrendData).toHaveBeenCalledTimes(1);
    expect(second.result.current.data?.points).toEqual([{ season: 2025, value: 4280 }]);
  });
});
