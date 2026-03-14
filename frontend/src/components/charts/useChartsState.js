import { useEffect, useState } from 'react';

import { useSessionStorageObject } from '../../hooks/useSessionStorageObject';
import { DEFAULT_STAT } from './chartsConfig';

const CHART_UI_STORAGE_KEY = 'chartsUi';

export function useChartsState() {
  const [chartUiState, setChartUiState] = useSessionStorageObject(CHART_UI_STORAGE_KEY, {});
  const initialPosition = chartUiState.position || 'Overall';

  const [view, setView] = useState(chartUiState.view || 'leaderboard');
  const [position, setPosition] = useState(initialPosition);
  const [season, setSeason] = useState(null);
  const [stat, setStat] = useState(chartUiState.stat || DEFAULT_STAT[initialPosition] || DEFAULT_STAT.Overall);
  const [topN, setTopN] = useState(chartUiState.topN || 20);
  const [trendPlayer, setTrendPlayer] = useState(chartUiState.trendPlayer || '');

  useEffect(() => {
    setChartUiState({ view, position, topN, stat, trendPlayer });
  }, [view, position, topN, stat, trendPlayer, setChartUiState]);

  return {
    view,
    setView,
    position,
    setPosition,
    season,
    setSeason,
    stat,
    setStat,
    topN,
    setTopN,
    trendPlayer,
    setTrendPlayer,
  };
}

export function useChartsStateValidation({
  view,
  stat,
  setStat,
  availableStatOptions,
  trendPlayer,
  setTrendPlayer,
  rankedTrendPlayers,
  trendPlayerOptions,
}) {
  useEffect(() => {
    if (!availableStatOptions.length) return;
    if (!availableStatOptions.includes(stat)) {
      setStat(availableStatOptions[0]);
    }
  }, [availableStatOptions, stat, setStat]);

  useEffect(() => {
    if (view !== 'trend') return;
    if (!trendPlayerOptions.length) {
      if (trendPlayer) setTrendPlayer('');
      return;
    }
    if (!trendPlayer || !trendPlayerOptions.includes(trendPlayer)) {
      setTrendPlayer(rankedTrendPlayers[0] || trendPlayerOptions[0]);
    }
  }, [view, trendPlayerOptions, rankedTrendPlayers, trendPlayer, setTrendPlayer]);
}
