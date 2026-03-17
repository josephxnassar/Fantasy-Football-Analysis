import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { deferred } from '../../../../support/deferred';
import { getPlayerTrendData } from '../../../../../src/api';
import { __resetSeasonTrendsDataCache, useSeasonTrendsData } from '../../../../../src/features/statistics/charts/season-trends/useSeasonTrendsData';
import { useStatisticsData } from '../../../../../src/features/statistics/useStatisticsData';

vi.mock('../../../../../src/api', () => ({
  getPlayerTrendData: vi.fn(),
}));

vi.mock('../../../../../src/features/statistics/useStatisticsData', () => ({
  useStatisticsData: vi.fn(),
}));

const STATISTICS_DATA_MOCK = {
  season: 2025,
  stat_columns: ['fp_ppr', 'pass_yds', 'rec_yds'],
  players: [
    { name: 'Patrick Mahomes', position: 'QB' },
    { name: 'Amon-Ra St. Brown', position: 'WR' },
    { name: 'Joe Burrow', position: 'QB' },
  ],
};

describe('useSeasonTrendsData', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    __resetSeasonTrendsDataCache();
    useStatisticsData.mockReturnValue({
      statisticsData: STATISTICS_DATA_MOCK,
      loading: false,
      error: null,
    });
  });

  it('loads season trend payload for the selected player + stat', async () => {
    getPlayerTrendData.mockResolvedValueOnce({
      data: {
        player_name: 'Patrick Mahomes',
        points: [{ season: 2025, value: 4280 }],
      },
    });

    const { result } = renderHook(() =>
      useSeasonTrendsData({
        stat: 'pass_yds',
        trendPlayer: 'Patrick Mahomes',
        enabled: true,
      }),
    );

    await waitFor(() => {
      expect(result.current.trendLoading).toBe(false);
    });

    expect(getPlayerTrendData).toHaveBeenCalledWith('Patrick Mahomes', 'QB', 'pass_yds');
    expect(result.current.trendSeries).toEqual([{ season: 2025, value: 4280 }]);
    expect(result.current.trendError).toBeNull();
  });

  it('skips fetch when disabled or query params are missing', async () => {
    const disabled = renderHook(() =>
      useSeasonTrendsData({
        stat: 'pass_yds',
        trendPlayer: 'Patrick Mahomes',
        enabled: false,
      }),
    );
    const missingPlayer = renderHook(() =>
      useSeasonTrendsData({
        stat: 'pass_yds',
        trendPlayer: '',
        enabled: true,
      }),
    );
    const missingStat = renderHook(() =>
      useSeasonTrendsData({
        stat: '',
        trendPlayer: 'Patrick Mahomes',
        enabled: true,
      }),
    );

    await waitFor(() => {
      expect(disabled.result.current.trendLoading).toBe(false);
      expect(missingPlayer.result.current.trendLoading).toBe(false);
      expect(missingStat.result.current.trendLoading).toBe(false);
    });

    expect(getPlayerTrendData).not.toHaveBeenCalled();
  });

  it('waits for the player pool to resolve before fetching trend data', async () => {
    useStatisticsData.mockReturnValue({
      statisticsData: null,
      loading: true,
      error: null,
    });

    const { result } = renderHook(() =>
      useSeasonTrendsData({
        stat: 'pass_yds',
        trendPlayer: 'Patrick Mahomes',
        enabled: true,
      }),
    );

    expect(result.current.trendLoading).toBe(true);
    expect(getPlayerTrendData).not.toHaveBeenCalled();
  });

  it('ignores stale responses when player changes mid-request', async () => {
    const firstRequest = deferred();
    const secondRequest = deferred();
    getPlayerTrendData.mockImplementationOnce(() => firstRequest.promise).mockImplementationOnce(() => secondRequest.promise);

    const { result, rerender } = renderHook(
      ({ trendPlayer }) =>
        useSeasonTrendsData({
          stat: 'pass_yds',
          trendPlayer,
          enabled: true,
        }),
      {
        initialProps: { trendPlayer: 'Patrick Mahomes' },
      },
    );

    rerender({ trendPlayer: 'Joe Burrow' });

    await waitFor(() => {
      expect(getPlayerTrendData).toHaveBeenCalledTimes(2);
    });

    await act(async () => {
      firstRequest.resolve({ data: { points: [{ season: 2025, value: 4280 }] } });
      await Promise.resolve();
    });

    expect(result.current.trendSeries).toEqual([]);

    await act(async () => {
      secondRequest.resolve({ data: { points: [{ season: 2025, value: 4650 }] } });
      await Promise.resolve();
    });

    await waitFor(() => {
      expect(result.current.trendLoading).toBe(false);
    });

    expect(result.current.trendSeries).toEqual([{ season: 2025, value: 4650 }]);
  });

  it('reuses cached payload for an identical trend query', async () => {
    getPlayerTrendData.mockResolvedValueOnce({
      data: { points: [{ season: 2025, value: 4280 }] },
    });

    const first = renderHook(() =>
      useSeasonTrendsData({
        stat: 'pass_yds',
        trendPlayer: 'Patrick Mahomes',
        enabled: true,
      }),
    );
    await waitFor(() => {
      expect(first.result.current.trendLoading).toBe(false);
    });
    first.unmount();

    const second = renderHook(() =>
      useSeasonTrendsData({
        stat: 'pass_yds',
        trendPlayer: 'Patrick Mahomes',
        enabled: true,
      }),
    );
    await waitFor(() => {
      expect(second.result.current.trendLoading).toBe(false);
    });

    expect(getPlayerTrendData).toHaveBeenCalledTimes(1);
    expect(second.result.current.trendSeries).toEqual([{ season: 2025, value: 4280 }]);
  });
});
