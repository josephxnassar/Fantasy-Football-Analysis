/**
 * File overview: Hook for Leaderboard Data within the leaderboard chart view.
 */

import { useMemo } from 'react';

import { getProductionGroupsWithoutRankings } from '../../../../shared/utils/statMeta';
import { useStatisticsData } from '../../useStatisticsData';
import { DEFAULT_STAT } from '../ChartsMeta';
import { buildBarData, getStatOptions } from '../chartsHelpers';

export function useLeaderboardData({ position, season, stat, enabled = true }) {
  const { statisticsData, loading, error } = useStatisticsData(position, season, enabled);
  const statGroups = useMemo(() => getProductionGroupsWithoutRankings(position), [position]);
  const barData = useMemo(() => buildBarData(statisticsData?.players, stat), [statisticsData?.players, stat]);
  const statOptions = useMemo(
    () => getStatOptions(statGroups, statisticsData?.stat_columns || []),
    [statGroups, statisticsData?.stat_columns],
  );
  const availableStatOptions = useMemo(() => statOptions.flatMap(({ stats }) => stats), [statOptions]);

  return {
    chartData: statisticsData,
    loading,
    error,
    barData,
    statOptions,
    defaultStat: DEFAULT_STAT[position] || DEFAULT_STAT.Overall,
    availableStatOptions,
    chartSeason: season ?? statisticsData?.season ?? null,
  };
}
