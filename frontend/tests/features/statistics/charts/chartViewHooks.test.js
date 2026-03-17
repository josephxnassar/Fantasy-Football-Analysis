import { renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { getConsistencyData, getPlayerTrendData } from '../../../../src/api';
import { useAverageVsUpsideData } from '../../../../src/features/statistics/charts/consistency-upside/useAverageVsUpsideData';
import { __resetAverageVsUpsideDataCache } from '../../../../src/features/statistics/charts/consistency-upside/useAverageVsUpsideData';
import { useLeaderboardData } from '../../../../src/features/statistics/charts/leaderboard/useLeaderboardData';
import { useSeasonTrendsData } from '../../../../src/features/statistics/charts/season-trends/useSeasonTrendsData';
import { __resetSeasonTrendsDataCache } from '../../../../src/features/statistics/charts/season-trends/useSeasonTrendsData';
import { useStatisticsData } from '../../../../src/features/statistics/useStatisticsData';

vi.mock('../../../../src/api', () => ({
  getConsistencyData: vi.fn(),
  getPlayerTrendData: vi.fn(),
}));

vi.mock('../../../../src/features/statistics/useStatisticsData', () => ({
  useStatisticsData: vi.fn(),
}));

describe('chart view hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    __resetAverageVsUpsideDataCache();
    __resetSeasonTrendsDataCache();
  });

  it('useSeasonTrendsData uses the overall player pool and derives stat groups from the selected player position', async () => {
    useStatisticsData.mockReturnValue({
      statisticsData: {
        season: 2025,
        stat_columns: ['fp_ppr', 'targets', 'rec_yds', 'rec_td'],
        players: [
          { name: 'Josh Allen', position: 'QB', team: 'BUF', stats: { fp_ppr: 402 } },
          { name: 'Amon-Ra St. Brown', position: 'WR', team: 'DET', stats: { fp_ppr: 301, targets: 145, rec_yds: 1263 } },
        ],
      },
      loading: false,
      error: null,
    });
    getPlayerTrendData.mockResolvedValue({
      data: { points: [] },
    });

    const { result } = renderHook(() =>
      useSeasonTrendsData({
        stat: 'pass_yds',
        trendPlayer: 'Amon-Ra St. Brown',
        enabled: true,
      }),
    );

    await waitFor(() => {
      expect(result.current.trendLoading).toBe(false);
    });

    expect(useStatisticsData).toHaveBeenCalledWith('Overall', null, true);
    expect(getPlayerTrendData).toHaveBeenCalledWith('Amon-Ra St. Brown', 'WR', 'pass_yds');
    expect(result.current.defaultStat).toBe('rec_yds');
    expect(result.current.trendPlayerOptions).toEqual(['Amon-Ra St. Brown', 'Josh Allen']);
    expect(result.current.statOptions.map((group) => group.category)).toEqual(['Fantasy', 'Receiving']);
  });

  it('useLeaderboardData keeps the selected position for leaderboard stats', () => {
    useStatisticsData.mockReturnValue({
      statisticsData: {
        season: 2025,
        stat_columns: ['fp_ppr', 'rush_yds'],
        players: [{ name: 'Saquon Barkley', position: 'RB', team: 'PHI', stats: { fp_ppr: 312, rush_yds: 1680 } }],
      },
      loading: false,
      error: null,
    });

    const { result } = renderHook(() =>
      useLeaderboardData({
        position: 'RB',
        season: 2025,
        stat: 'rush_yds',
        enabled: true,
      }),
    );

    expect(useStatisticsData).toHaveBeenCalledWith('RB', 2025, true);
    expect(result.current.defaultStat).toBe('rush_yds');
    expect(result.current.statOptions.map((group) => group.category)).toEqual(['Fantasy', 'Rushing']);
  });

  it('useAverageVsUpsideData follows the selected position through the consistency request', async () => {
    useStatisticsData.mockReturnValue({
      statisticsData: {
        season: 2025,
        players: [],
      },
      loading: false,
      error: null,
    });
    getConsistencyData.mockResolvedValue({
      data: { players: [{ name: 'JaMarr Chase' }] },
    });

    const { result } = renderHook(() =>
      useAverageVsUpsideData({
        position: 'WR',
        season: 2025,
        enabled: true,
      }),
    );

    await waitFor(() => {
      expect(result.current.consistencyLoading).toBe(false);
    });

    expect(useStatisticsData).toHaveBeenCalledWith('WR', 2025, true);
    expect(getConsistencyData).toHaveBeenCalledWith('WR', 2025, 50);
    expect(result.current.consistencyData).toEqual({ players: [{ name: 'JaMarr Chase' }] });
  });
});
