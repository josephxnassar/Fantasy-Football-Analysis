import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { deferred } from '../../support/deferred';
import { useTeamModalData } from '../../../src/shared/hooks/useTeamModalData';

describe('useTeamModalData', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('skips fetch and clears loading when no team is provided', async () => {
    const fetchFn = vi.fn();
    const { result } = renderHook(() => useTeamModalData('', fetchFn, 'Failed to load data.'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(fetchFn).not.toHaveBeenCalled();
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('loads team data successfully', async () => {
    const fetchFn = vi.fn().mockResolvedValue({
      data: { team: 'KC', opponents: ['BUF', 'DEN'] },
    });
    const { result } = renderHook(() => useTeamModalData('KC', fetchFn, 'Failed to load data.'));

    await waitFor(() => {
      expect(fetchFn).toHaveBeenCalledWith('KC');
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual({ team: 'KC', opponents: ['BUF', 'DEN'] });
    expect(result.current.error).toBeNull();
  });

  it('ignores stale responses when the selected team changes', async () => {
    const firstRequest = deferred();
    const secondRequest = deferred();
    const fetchFn = vi.fn()
      .mockImplementationOnce(() => firstRequest.promise)
      .mockImplementationOnce(() => secondRequest.promise);

    const { result, rerender } = renderHook(
      ({ team }) => useTeamModalData(team, fetchFn, 'Failed to load data.'),
      { initialProps: { team: 'KC' } }
    );

    rerender({ team: 'BUF' });

    await waitFor(() => {
      expect(fetchFn).toHaveBeenCalledTimes(2);
    });

    await act(async () => {
      firstRequest.resolve({ data: { team: 'KC' } });
      await Promise.resolve();
    });

    expect(result.current.data).toBeNull();

    await act(async () => {
      secondRequest.resolve({ data: { team: 'BUF' } });
      await Promise.resolve();
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual({ team: 'BUF' });
    expect(result.current.error).toBeNull();
  });

  it('exposes error state when fetch fails', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    const fetchFn = vi.fn().mockRejectedValue(new Error('Server error'));
    const { result } = renderHook(() => useTeamModalData('KC', fetchFn, 'Failed to load data.'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Failed to load data.');
    expect(result.current.data).toBeNull();
  });

  it('clears stale data when a refetch fails', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    const fetchFn = vi.fn()
      .mockResolvedValueOnce({ data: { team: 'KC', opponents: ['BUF'] } })
      .mockRejectedValueOnce(new Error('Server error'));

    const { result, rerender } = renderHook(
      ({ team }) => useTeamModalData(team, fetchFn, 'Failed to load data.'),
      { initialProps: { team: 'KC' } }
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual({ team: 'KC', opponents: ['BUF'] });

    rerender({ team: 'BUF' });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Failed to load data.');
    expect(result.current.data).toBeNull();
  });
});
