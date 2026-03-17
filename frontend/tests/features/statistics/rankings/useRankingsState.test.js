import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';

import { useRankingsState } from '../../../../src/features/statistics/rankings/useRankingsState';

describe('useRankingsState', () => {
  beforeEach(() => {
    window.sessionStorage.clear();
  });

  it('hydrates legacy overall-only weight storage and rewrites it to the flat shape', async () => {
    window.sessionStorage.setItem(
      'rankingsWeights',
      JSON.stringify({
        Overall: {
          categoryWeights: { 'Fantasy Output': 2 },
          statWeights: { fp_ppr: 1 },
        },
      }),
    );

    const { result } = renderHook(() => useRankingsState());

    expect(result.current.categoryWeights).toEqual({ 'Fantasy Output': 2 });
    expect(result.current.statWeights).toEqual({ fp_ppr: 1 });

    await waitFor(() => {
      expect(window.sessionStorage.getItem('rankingsWeights')).toBe(
        JSON.stringify({
          categoryWeights: { 'Fantasy Output': 2 },
          statWeights: { fp_ppr: 1 },
        }),
      );
    });
  });

  it('persists flat weight storage for new updates', async () => {
    const { result } = renderHook(() => useRankingsState());

    act(() => {
      result.current.setCategoryWeight('Fantasy Output', 2);
      result.current.setStatWeight('fp_ppr', 1);
    });

    await waitFor(() => {
      expect(window.sessionStorage.getItem('rankingsWeights')).toBe(
        JSON.stringify({
          categoryWeights: { 'Fantasy Output': 2 },
          statWeights: { fp_ppr: 1 },
        }),
      );
    });
  });
});
