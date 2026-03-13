import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { deferred } from '../deferred';
import { __resetChartDataCache, useChartData } from '../../src/hooks/useChartData';
import { getChartData } from '../../src/api';

vi.mock('../../src/api', () => ({
  getChartData: vi.fn(),
}));

describe('useChartData', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    __resetChartDataCache();
  });

  it('loads chart data for a position and season', async () => {
    getChartData.mockResolvedValueOnce({
      data: { labels: ['Player A'], values: [100] },
    });

    const { result } = renderHook(() => useChartData('QB', 2024));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(getChartData).toHaveBeenCalledWith('QB', 2024);
    expect(result.current.chartData).toEqual({ labels: ['Player A'], values: [100] });
    expect(result.current.error).toBeNull();
  });

  it('exposes error message on fetch failure', async () => {
    getChartData.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useChartData('RB', 2024));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.chartData).toBeNull();
  });

  it('ignores stale responses when position changes mid-request', async () => {
    const firstRequest = deferred();
    const secondRequest = deferred();
    getChartData
      .mockImplementationOnce(() => firstRequest.promise)
      .mockImplementationOnce(() => secondRequest.promise);

    const { result, rerender } = renderHook(
      ({ position }) => useChartData(position, 2024),
      { initialProps: { position: 'QB' } }
    );

    rerender({ position: 'RB' });

    await waitFor(() => {
      expect(getChartData).toHaveBeenCalledTimes(2);
    });

    // Resolve first (stale) request — should be ignored.
    await act(async () => {
      firstRequest.resolve({ data: { labels: ['QB Player'] } });
      await Promise.resolve();
    });

    expect(result.current.chartData).toBeNull();

    // Resolve second (current) request.
    await act(async () => {
      secondRequest.resolve({ data: { labels: ['RB Player'] } });
      await Promise.resolve();
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.chartData).toEqual({ labels: ['RB Player'] });
  });

  it('reuses cached payload for identical position + season', async () => {
    getChartData.mockResolvedValueOnce({
      data: { labels: ['Cached Player'] },
    });

    const first = renderHook(() => useChartData('WR', 2025));
    await waitFor(() => {
      expect(first.result.current.loading).toBe(false);
    });
    first.unmount();

    const second = renderHook(() => useChartData('WR', 2025));
    await waitFor(() => {
      expect(second.result.current.loading).toBe(false);
    });

    expect(getChartData).toHaveBeenCalledTimes(1);
    expect(second.result.current.chartData).toEqual({ labels: ['Cached Player'] });
  });
});
