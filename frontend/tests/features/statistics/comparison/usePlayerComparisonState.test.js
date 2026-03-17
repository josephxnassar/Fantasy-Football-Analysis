import { renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useStatisticsData } from '../../../../src/features/statistics/useStatisticsData';
import { usePlayerComparisonState } from '../../../../src/features/statistics/comparison/usePlayerComparisonState';
import { useComparisonSlots } from '../../../../src/features/statistics/comparison/useComparisonSlots';

vi.mock('../../../../src/features/statistics/useStatisticsData', () => ({
  useStatisticsData: vi.fn(),
}));

vi.mock('../../../../src/features/statistics/comparison/useComparisonSlots', () => ({
  MAX_COMPARE_PLAYERS: 3,
  useComparisonSlots: vi.fn(),
}));

describe('usePlayerComparisonState', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useStatisticsData.mockReturnValue({
      statisticsData: { players: [] },
      loading: false,
      error: null,
    });
  });

  it('shows a detecting label while selected players are still loading their position', () => {
    useComparisonSlots.mockReturnValue({
      comparisonSlots: [
        {
          id: 1,
          playerName: 'Josh Allen',
          position: null,
          loading: true,
          error: null,
          season: null,
          weeksPlayed: null,
          stats: null,
        },
      ],
      selectionError: null,
      handlePlayerSelect: vi.fn(),
      handleSeasonChange: vi.fn(),
      handleRemovePlayer: vi.fn(),
    });

    const { result } = renderHook(() => usePlayerComparisonState());

    expect(result.current.comparisonProfileLabel).toBe('Detecting...');
  });
});
