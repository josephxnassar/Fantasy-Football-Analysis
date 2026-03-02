import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { deferred } from '../../setup';
import { useTeamDepthChart } from '../../../src/hooks/useTeamDepthChart';
import { getTeamDepthChart } from '../../../src/api';

vi.mock('../../../src/api', () => ({
  getTeamDepthChart: vi.fn(),
}));

describe('useTeamDepthChart', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('does not fetch when no team is selected', () => {
    const { result } = renderHook(() => useTeamDepthChart(''));

    expect(getTeamDepthChart).not.toHaveBeenCalled();
    expect(result.current.teamDepthChart).toBeNull();
    expect(result.current.depthChartLoading).toBe(false);
  });

  it('loads depth chart data for a selected team', async () => {
    getTeamDepthChart.mockResolvedValueOnce({
      data: { team: 'KC', starters: { QB: 'Patrick Mahomes' } },
    });

    const { result } = renderHook(() => useTeamDepthChart('KC'));

    await waitFor(() => {
      expect(getTeamDepthChart).toHaveBeenCalledWith('KC');
      expect(result.current.depthChartLoading).toBe(false);
    });

    expect(result.current.teamDepthChart).toEqual({
      team: 'KC',
      starters: { QB: 'Patrick Mahomes' },
    });
  });

  it('ignores stale responses when team changes mid-request', async () => {
    const firstRequest = deferred();
    const secondRequest = deferred();
    getTeamDepthChart
      .mockImplementationOnce(() => firstRequest.promise)
      .mockImplementationOnce(() => secondRequest.promise);

    const { result, rerender } = renderHook(
      ({ team }) => useTeamDepthChart(team),
      { initialProps: { team: 'KC' } }
    );

    rerender({ team: 'BUF' });

    await waitFor(() => {
      expect(getTeamDepthChart).toHaveBeenCalledTimes(2);
    });

    await act(async () => {
      firstRequest.resolve({ data: { team: 'KC' } });
      await Promise.resolve();
    });

    expect(result.current.teamDepthChart).toBeNull();

    await act(async () => {
      secondRequest.resolve({ data: { team: 'BUF' } });
      await Promise.resolve();
    });

    await waitFor(() => {
      expect(result.current.depthChartLoading).toBe(false);
    });

    expect(result.current.teamDepthChart).toEqual({ team: 'BUF' });
  });

  it('exposes error state when fetch fails', async () => {
    getTeamDepthChart.mockRejectedValueOnce(new Error('Server error'));

    const { result } = renderHook(() => useTeamDepthChart('KC'));

    await waitFor(() => {
      expect(result.current.depthChartLoading).toBe(false);
    });

    expect(result.current.depthChartError).toBe('Failed to load depth chart');
    expect(result.current.teamDepthChart).toBeNull();
  });
});
