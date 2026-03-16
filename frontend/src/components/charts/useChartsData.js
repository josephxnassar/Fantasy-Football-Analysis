import { useMemo } from 'react';

import { useChartData } from '../../hooks/useChartData';
import { PRODUCTION_GROUPS_NO_RANKS } from '../../utils/statMeta';
import { buildBarData, getStatOptions } from './chartsHelpers';
import { useConsistencyData } from './useConsistencyData';
import { useSeasonChartData } from './useSeasonChartData';

export function useChartsData({ view, position, season, stat, topN, trendPlayer }) {
  const effectiveSeason = view === 'trend' ? null : season;
  const { chartData, loading, error } = useChartData(position, effectiveSeason);
  const consistencyEnabled = view === 'consistency-upside';
  const trendEnabled = view === 'trend';
  const consistency = useConsistencyData(position, effectiveSeason, topN, consistencyEnabled);
  const trend = useSeasonChartData(position, trendPlayer, stat, trendEnabled);

  const barData = useMemo(() => buildBarData(chartData?.players, stat, topN), [chartData?.players, stat, topN]);
  const statOptions = useMemo(() => getStatOptions(position, chartData?.stat_columns || [], PRODUCTION_GROUPS_NO_RANKS), [position, chartData?.stat_columns]);
  const availableStatOptions = useMemo(() => statOptions.flatMap(({ stats }) => stats), [statOptions]);
  const rankedTrendPlayers = useMemo(() => buildBarData(chartData?.players, stat, chartData?.players?.length || 0).map((row) => row.name), [chartData?.players, stat]);
  const trendPlayerOptions = useMemo(() => rankedTrendPlayers.slice().sort((a, b) => a.localeCompare(b)), [rankedTrendPlayers]);

  return {
    chartData,
    loading,
    error,
    consistencyEnabled,
    consistencyData: consistency.data,
    consistencyLoading: consistency.loading,
    consistencyError: consistency.error,
    trendEnabled,
    trendData: trend.data,
    trendLoading: trend.loading,
    trendError: trend.error,
    barData,
    statOptions,
    availableStatOptions,
    rankedTrendPlayers,
    trendPlayerOptions,
    trendSeries: trend.data?.points || [],
    chartSeason: effectiveSeason ?? chartData?.season ?? null,
  };
}
