import { describe, expect, it } from 'vitest';

import { getStatColorClass } from '../../../src/utils/statColorHelpers';

describe('getStatColorClass', () => {
  describe('invalid inputs', () => {
    it('returns empty string for null', () => {
      expect(getStatColorClass('fp_ppr', null)).toBe('');
    });

    it('returns empty string for undefined', () => {
      expect(getStatColorClass('fp_ppr', undefined)).toBe('');
    });

    it('returns empty string for NaN', () => {
      expect(getStatColorClass('fp_ppr', NaN)).toBe('');
    });

    it('returns empty string for Infinity', () => {
      expect(getStatColorClass('fp_ppr', Infinity)).toBe('');
    });
  });

  describe('threshold-based stats', () => {
    it('returns stat-good when value meets threshold', () => {
      expect(getStatColorClass('fp_ppr', 25)).toBe('stat-good');
    });

    it('returns stat-medium when value is between 50% and 100% of threshold', () => {
      expect(getStatColorClass('fp_ppr', 12)).toBe('stat-medium');
    });

    it('returns stat-poor when value is below 50% of threshold', () => {
      expect(getStatColorClass('fp_ppr', 5)).toBe('stat-poor');
    });

    it('handles passing yards threshold', () => {
      expect(getStatColorClass('pass_yds', 350)).toBe('stat-good');
      expect(getStatColorClass('pass_yds', 200)).toBe('stat-medium');
      expect(getStatColorClass('pass_yds', 100)).toBe('stat-poor');
    });
  });

  describe('lower-is-better stats', () => {
    it('returns stat-good for zero interceptions', () => {
      expect(getStatColorClass('interception', 0)).toBe('stat-good');
    });

    it('returns stat-medium for one interception', () => {
      expect(getStatColorClass('interception', 1)).toBe('stat-medium');
    });

    it('returns stat-poor for multiple interceptions', () => {
      expect(getStatColorClass('interception', 3)).toBe('stat-poor');
    });

    it('handles percent-based lower-is-better stats', () => {
      expect(getStatColorClass('bad_throw_pct', 5)).toBe('stat-good');
      expect(getStatColorClass('bad_throw_pct', 15)).toBe('stat-medium');
      expect(getStatColorClass('bad_throw_pct', 25)).toBe('stat-poor');
    });

    it('normalizes ratio-form lower-is-better percent stats', () => {
      // 0.08 → 8% → stat-good (<=10)
      expect(getStatColorClass('pressure_pct', 0.08)).toBe('stat-good');
    });
  });

  describe('rank stats', () => {
    it('returns stat-good for top ranks', () => {
      expect(getStatColorClass('fp_ppr_rank', 5)).toBe('stat-good');
    });

    it('returns stat-medium for mid ranks', () => {
      expect(getStatColorClass('fp_ppr_rank', 15)).toBe('stat-medium');
    });

    it('returns stat-poor for low ranks', () => {
      expect(getStatColorClass('fp_ppr_rank', 25)).toBe('stat-poor');
    });
  });

  describe('generic percent fallbacks', () => {
    it('returns stat-good for unknown percent stat above 80', () => {
      expect(getStatColorClass('custom_metric_pct', 85)).toBe('stat-good');
    });

    it('returns stat-medium for unknown percent stat 60-80', () => {
      expect(getStatColorClass('custom_metric_pct', 65)).toBe('stat-medium');
    });

    it('returns stat-poor for unknown percent stat below 60', () => {
      expect(getStatColorClass('custom_metric_pct', 40)).toBe('stat-poor');
    });
  });

  describe('keyword fallbacks', () => {
    it('scores touchdown stats by keyword', () => {
      expect(getStatColorClass('some_td', 2)).toBe('stat-good');
      expect(getStatColorClass('some_td', 1)).toBe('stat-medium');
      expect(getStatColorClass('some_td', 0)).toBe('stat-poor');
    });

    it('scores yardage stats by keyword', () => {
      expect(getStatColorClass('some_yds', 120)).toBe('stat-good');
      expect(getStatColorClass('some_yds', 60)).toBe('stat-medium');
      expect(getStatColorClass('some_yds', 30)).toBe('stat-poor');
    });

    it('scores attempt stats by keyword', () => {
      expect(getStatColorClass('some_att', 25)).toBe('stat-good');
      expect(getStatColorClass('some_att', 15)).toBe('stat-medium');
      expect(getStatColorClass('some_att', 5)).toBe('stat-poor');
    });
  });

  describe('generic fallback', () => {
    it('returns stat-poor for negative values', () => {
      expect(getStatColorClass('unknown_metric', -5)).toBe('stat-poor');
    });

    it('returns stat-poor for zero', () => {
      expect(getStatColorClass('unknown_metric', 0)).toBe('stat-poor');
    });

    it('returns stat-medium for small positive values', () => {
      expect(getStatColorClass('unknown_metric', 0.5)).toBe('stat-medium');
    });

    it('returns stat-good for larger positive values', () => {
      expect(getStatColorClass('unknown_metric', 10)).toBe('stat-good');
    });
  });

  describe('string coercion', () => {
    it('handles numeric strings', () => {
      expect(getStatColorClass('fp_ppr', '25')).toBe('stat-good');
    });

    it('returns empty for non-numeric strings', () => {
      expect(getStatColorClass('fp_ppr', 'abc')).toBe('');
    });
  });
});
