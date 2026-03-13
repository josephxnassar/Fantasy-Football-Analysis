import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { deferred } from '../../deferred';
import { getAppInfo } from '../../../src/api';

vi.mock('../../../src/api', () => ({
  getAppInfo: vi.fn(),
}));

describe('useAppInfo', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  const mockResponse = {
    data: {
      total_players: 2500,
      current_season_players: 1800,
      seasons: [2021, 2022, 2023, 2024, 2025],
      current_season: 2025,
      total_game_logs: 42000,
      stat_columns: 67,
      rookie_count: 312,
    },
  };

  it('loads app info and exposes the payload', async () => {
    getAppInfo.mockResolvedValueOnce(mockResponse);
    const { useAppInfo } = await import('../../../src/components/landing/useAppInfo');

    const { result } = renderHook(() => useAppInfo());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(getAppInfo).toHaveBeenCalledTimes(1);
    expect(result.current.data).toEqual(mockResponse.data);
    expect(result.current.error).toBeNull();
  });

  it('reuses cached app info on later mounts without another API call', async () => {
    getAppInfo.mockResolvedValueOnce(mockResponse);
    const { useAppInfo } = await import('../../../src/components/landing/useAppInfo');

    const { result, unmount } = renderHook(() => useAppInfo());
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    unmount();

    const { result: secondResult } = renderHook(() => useAppInfo());
    await waitFor(() => {
      expect(secondResult.current.loading).toBe(false);
    });

    expect(getAppInfo).toHaveBeenCalledTimes(1);
    expect(secondResult.current.data).toEqual(mockResponse.data);
  });

  it('shares a single in-flight request across concurrent mounts', async () => {
    const pendingRequest = deferred();
    getAppInfo.mockImplementationOnce(() => pendingRequest.promise);
    const { useAppInfo } = await import('../../../src/components/landing/useAppInfo');

    const first = renderHook(() => useAppInfo());
    const second = renderHook(() => useAppInfo());

    await waitFor(() => {
      expect(getAppInfo).toHaveBeenCalledTimes(1);
    });

    await act(async () => {
      pendingRequest.resolve(mockResponse);
      await Promise.resolve();
    });

    await waitFor(() => {
      expect(first.result.current.loading).toBe(false);
      expect(second.result.current.loading).toBe(false);
    });

    expect(first.result.current.data).toEqual(mockResponse.data);
    expect(second.result.current.data).toEqual(mockResponse.data);
  });

  it('exposes an error state when the request fails', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    getAppInfo.mockRejectedValueOnce(new Error('App info failed'));
    const { useAppInfo } = await import('../../../src/components/landing/useAppInfo');

    const { result } = renderHook(() => useAppInfo());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBeNull();
    expect(result.current.error).toBe('Failed to load app info');
  });
});
