import { describe, expect, it } from 'vitest';

import { isLowerBetterStat } from '../../../src/utils/statDirection';

describe('isLowerBetterStat', () => {
  it('treats time-to-throw as lower-is-better', () => {
    expect(isLowerBetterStat('ng_pass_avg_time_to_throw')).toBe(true);
  });

  it('does not mark common higher-is-better stats as lower-is-better', () => {
    expect(isLowerBetterStat('pass_td')).toBe(false);
  });
});
