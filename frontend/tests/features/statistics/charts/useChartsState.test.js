import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';

import { DEFAULT_STAT } from '../../../../src/features/statistics/charts/ChartsMeta';
import { getNextChartStat, getNextTrendPlayer, useChartsState } from '../../../../src/features/statistics/charts/useChartsState';

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
        stat: 'target_share',
        trendPlayer: 'JaMarr Chase',
      }),
    );

    const { result } = renderHook(() => useChartsState());

    expect(result.current.view).toBe('trend');
    expect(result.current.position).toBe('WR');
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
      result.current.setStat('pass_td');
      result.current.setTrendPlayer('Josh Allen');
    });

    await waitFor(() => {
      expect(window.sessionStorage.getItem('chartsUi')).toBe(
        JSON.stringify({
          view: 'trend',
          position: 'QB',
          stat: 'pass_td',
          trendPlayer: 'Josh Allen',
        }),
      );
    });
  });
});

describe('chart selection helpers', () => {
  it('keeps a valid stat selection unchanged', () => {
    expect(getNextChartStat('rush_yds', 'fp_ppr', ['fp_ppr', 'rush_yds'])).toBe('rush_yds');
  });

  it('falls back to the default stat when the current stat is unavailable', () => {
    expect(getNextChartStat('pass_td', 'rec_yds', ['fp_ppr', 'rec_yds'])).toBe('rec_yds');
  });

  it('keeps the stored trend player while trend options are still loading', () => {
    expect(getNextTrendPlayer('trend', 'Josh Allen', [], true)).toBe('Josh Allen');
  });

  it('clears the stored trend player once loading is done and no options remain', () => {
    expect(getNextTrendPlayer('trend', 'Josh Allen', [], false)).toBe('');
  });
});
