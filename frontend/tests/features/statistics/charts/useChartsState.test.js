import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';

import { DEFAULT_STAT } from '../../../../src/features/statistics/charts/chartsConfig';
import { useChartsState } from '../../../../src/features/statistics/charts/useChartsState';

describe('useChartsState', () => {
  beforeEach(() => {
    window.sessionStorage.clear();
  });

  it('hydrates chart controls from sessionStorage when available', () => {
    window.sessionStorage.setItem(
      'chartsUi',
      JSON.stringify({
        view: 'trend',
        position: 'WR',
        topN: 35,
        stat: 'target_share',
        trendPlayer: 'JaMarr Chase',
      })
    );

    const { result } = renderHook(() => useChartsState());

    expect(result.current.view).toBe('trend');
    expect(result.current.position).toBe('WR');
    expect(result.current.topN).toBe(35);
    expect(result.current.stat).toBe('target_share');
    expect(result.current.trendPlayer).toBe('JaMarr Chase');
  });

  it('uses position defaults for stat when stored stat is missing', () => {
    window.sessionStorage.setItem('chartsUi', JSON.stringify({ position: 'RB' }));

    const { result } = renderHook(() => useChartsState());

    expect(result.current.position).toBe('RB');
    expect(result.current.stat).toBe(DEFAULT_STAT.RB);
  });

  it('persists chart UI changes back to sessionStorage', async () => {
    const { result } = renderHook(() => useChartsState());

    act(() => {
      result.current.setView('trend');
      result.current.setPosition('QB');
      result.current.setTopN(12);
      result.current.setStat('pass_td');
      result.current.setTrendPlayer('Josh Allen');
    });

    await waitFor(() => {
      expect(window.sessionStorage.getItem('chartsUi')).toBe(
        JSON.stringify({
          view: 'trend',
          position: 'QB',
          topN: 12,
          stat: 'pass_td',
          trendPlayer: 'Josh Allen',
        })
      );
    });
  });
});

