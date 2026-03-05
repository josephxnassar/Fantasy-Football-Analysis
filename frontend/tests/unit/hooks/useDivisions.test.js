import { renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { getDivisions } from '../../../src/api';

vi.mock('../../../src/api', () => ({
  getDivisions: vi.fn(),
}));

describe('useDivisions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  const mockResponse = {
    data: {
      divisions: {
        AFC: { East: ['BUF', 'MIA', 'NE', 'NYJ'] },
      },
      team_names: { BUF: 'Buffalo Bills', MIA: 'Miami Dolphins' },
    },
  };

  it('loads divisions and exposes team data', async () => {
    getDivisions.mockResolvedValueOnce(mockResponse);
    const { useDivisions } = await import('../../../src/hooks/useDivisions');

    const { result } = renderHook(() => useDivisions());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(getDivisions).toHaveBeenCalledTimes(1);
    expect(result.current.divisions).toEqual(mockResponse.data.divisions);
    expect(result.current.teamNames).toEqual(mockResponse.data.team_names);
    expect(result.current.allTeams).toEqual(['BUF', 'MIA', 'NE', 'NYJ']);
    expect(result.current.error).toBeNull();
  });

  it('reuses cached data on second mount without calling API again', async () => {
    getDivisions.mockResolvedValueOnce(mockResponse);
    const { useDivisions } = await import('../../../src/hooks/useDivisions');

    const { result, unmount } = renderHook(() => useDivisions());
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    unmount();

    const { result: result2 } = renderHook(() => useDivisions());
    await waitFor(() => {
      expect(result2.current.loading).toBe(false);
    });

    expect(getDivisions).toHaveBeenCalledTimes(1);
    expect(result2.current.divisions).toEqual(mockResponse.data.divisions);
  });

  it('exposes error state when fetch fails', async () => {
    getDivisions.mockRejectedValueOnce(new Error('Network error'));
    vi.spyOn(console, 'error').mockImplementation(() => {});
    const { useDivisions } = await import('../../../src/hooks/useDivisions');

    const { result } = renderHook(() => useDivisions());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Failed to load division data');
    expect(result.current.divisions).toBeNull();
  });
});
