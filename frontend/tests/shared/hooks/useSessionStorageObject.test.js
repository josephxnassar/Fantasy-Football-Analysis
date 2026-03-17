import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';

import { useSessionStorageObject } from '../../../src/shared/hooks/useSessionStorageObject';

describe('useSessionStorageObject', () => {
  beforeEach(() => {
    window.sessionStorage.clear();
  });

  it('uses default object when no stored value exists', () => {
    const { result } = renderHook(() => useSessionStorageObject('chartsUi', { view: 'leaderboard' }));

    expect(result.current[0]).toEqual({ view: 'leaderboard' });
  });

  it('loads stored object when JSON is valid', () => {
    window.sessionStorage.setItem('chartsUi', JSON.stringify({ view: 'trend', position: 'WR' }));

    const { result } = renderHook(() => useSessionStorageObject('chartsUi', { view: 'leaderboard' }));

    expect(result.current[0]).toEqual({ view: 'trend', position: 'WR' });
  });

  it('falls back to default when stored JSON is invalid or not an object', () => {
    window.sessionStorage.setItem('chartsUi', '"not-an-object"');

    const { result } = renderHook(() => useSessionStorageObject('chartsUi', { view: 'leaderboard' }));

    expect(result.current[0]).toEqual({ view: 'leaderboard' });
  });

  it('persists updated values into sessionStorage', async () => {
    const { result } = renderHook(() => useSessionStorageObject('chartsUi', { view: 'leaderboard' }));

    act(() => {
      result.current[1]({ view: 'trend', stat: 'pass_td' });
    });

    await waitFor(() => {
      expect(window.sessionStorage.getItem('chartsUi')).toBe(JSON.stringify({ view: 'trend', stat: 'pass_td' }));
    });
  });
});
