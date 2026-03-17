import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { getChartData } from '../../../src/api';
import { deferred } from '../../support/deferred';
import { __resetStatisticsDataCache, useStatisticsData } from '../../../src/features/statistics/useStatisticsData';

vi.mock('../../../src/api', () => ({
  getChartData: vi.fn(),
}));

describe('useStatisticsData', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    __resetStatisticsDataCache();
  });

  it('loads statistics data for a position and season', async () => {
    getChartData.mockResolvedValueOnce({
      data: { labels: ['Player A'], values: [100] },
    });

    const { result } = renderHook(() => useStatisticsData('QB', 2024));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(getChartData).toHaveBeenCalledWith('QB', 2024);
    expect(result.current.statisticsData).toEqual({ labels: ['Player A'], values: [100] });
    expect(result.current.error).toBeNull();
  });

  it('exposes error message on fetch failure', async () => {
    getChartData.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useStatisticsData('RB', 2024));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.statisticsData).toBeNull();
  });

  it('ignores stale responses when position changes mid-request', async () => {
    const firstRequest = deferred();
    const secondRequest = deferred();
    getChartData.mockImplementationOnce(() => firstRequest.promise).mockImplementationOnce(() => secondRequest.promise);

    const { result, rerender } = renderHook(({ position }) => useStatisticsData(position, 2024), {
      initialProps: { position: 'QB' },
    });

    rerender({ position: 'RB' });

    await waitFor(() => {
      expect(getChartData).toHaveBeenCalledTimes(2);
    });

    await act(async () => {
      firstRequest.resolve({ data: { labels: ['QB Player'] } });
      await Promise.resolve();
    });

    expect(result.current.statisticsData).toBeNull();

    await act(async () => {
      secondRequest.resolve({ data: { labels: ['RB Player'] } });
      await Promise.resolve();
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.statisticsData).toEqual({ labels: ['RB Player'] });
  });

  it('reuses cached payload for identical position + season', async () => {
    getChartData.mockResolvedValueOnce({
      data: { labels: ['Cached Player'] },
    });

    const first = renderHook(() => useStatisticsData('WR', 2025));
    await waitFor(() => {
      expect(first.result.current.loading).toBe(false);
    });
    first.unmount();

    const second = renderHook(() => useStatisticsData('WR', 2025));
    await waitFor(() => {
      expect(second.result.current.loading).toBe(false);
    });

    expect(getChartData).toHaveBeenCalledTimes(1);
    expect(second.result.current.statisticsData).toEqual({ labels: ['Cached Player'] });
  });

  it('stays idle when disabled', async () => {
    const { result } = renderHook(() => useStatisticsData('WR', 2025, false));

    expect(getChartData).not.toHaveBeenCalled();
    expect(result.current.statisticsData).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('reports loading immediately when re-enabled without cached data', async () => {
    const request = deferred();
    getChartData.mockImplementation(() => request.promise);

    const { result, rerender } = renderHook(({ enabled }) => useStatisticsData('WR', 2025, enabled), {
      initialProps: { enabled: false },
    });

    rerender({ enabled: true });

    expect(result.current.loading).toBe(true);
    await waitFor(() => {
      expect(getChartData).toHaveBeenCalledWith('WR', 2025);
    });
  });
});
