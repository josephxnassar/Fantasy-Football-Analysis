import { describe, expect, it } from 'vitest';

import { CHART_VIEW_OPTIONS, VIEW_META, VIEWS_USING_STAT } from '../../../../src/features/statistics/charts/ChartsMeta';

describe('ChartsMeta', () => {
  it('defines the supported chart views in display order', () => {
    expect(CHART_VIEW_OPTIONS).toEqual([
      { value: 'leaderboard', label: 'Leaderboard' },
      { value: 'consistency-upside', label: 'Average vs Upside' },
      { value: 'trend', label: 'Season Trends' },
    ]);
  });

  it('provides metadata for every chart view', () => {
    const viewValues = CHART_VIEW_OPTIONS.map((option) => option.value);
    viewValues.forEach((value) => {
      expect(VIEW_META[value]).toBeDefined();
      expect(typeof VIEW_META[value].description).toBe('string');
      expect(VIEW_META[value].description.length).toBeGreaterThan(0);
    });
    expect(VIEW_META['consistency-upside'].kicker).toBe('Average vs Upside');
    expect(VIEW_META.trend.kicker).toBe('Season Trends');
  });

  it('tracks which views expose the stat control', () => {
    expect(VIEWS_USING_STAT.has('leaderboard')).toBe(true);
    expect(VIEWS_USING_STAT.has('trend')).toBe(true);
    expect(VIEWS_USING_STAT.has('consistency-upside')).toBe(false);
  });
});
