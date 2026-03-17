import { useEffect, useState } from 'react';

import { useSessionStorageObject } from '../../../shared/hooks/useSessionStorageObject';
import { DEFAULT_STAT } from './ChartsMeta';

const CHART_UI_STORAGE_KEY = 'chartsUi';

export function useChartsState() {
  const [chartUiState, setChartUiState] = useSessionStorageObject(CHART_UI_STORAGE_KEY, {});
  const initialPosition = chartUiState.position || 'Overall';

  const [view, setView] = useState(chartUiState.view || 'leaderboard');
  const [position, setPosition] = useState(initialPosition);
  const [season, setSeason] = useState(null);
  const [stat, setStat] = useState(chartUiState.stat || DEFAULT_STAT[initialPosition] || DEFAULT_STAT.Overall);
  const [trendPlayer, setTrendPlayer] = useState(chartUiState.trendPlayer || '');

  useEffect(() => {
    setChartUiState({ view, position, stat, trendPlayer });
  }, [view, position, stat, trendPlayer, setChartUiState]);

  return {
    view,
    setView,
    position,
    setPosition,
    season,
    setSeason,
    stat,
    setStat,
    trendPlayer,
    setTrendPlayer,
  };
}

export function getNextChartStat(stat, defaultStat, availableStatOptions) {
  if (!availableStatOptions.length || availableStatOptions.includes(stat)) return stat;
  if (availableStatOptions.includes(defaultStat)) return defaultStat;
  return availableStatOptions[0];
}

export function getNextTrendPlayer(view, trendPlayer, trendPlayerOptions, trendPlayerOptionsLoading = false) {
  if (view !== 'trend' || trendPlayerOptionsLoading) return trendPlayer;
  if (!trendPlayerOptions.length) return '';
  if (trendPlayer && trendPlayerOptions.includes(trendPlayer)) return trendPlayer;
  return trendPlayerOptions[0];
}
