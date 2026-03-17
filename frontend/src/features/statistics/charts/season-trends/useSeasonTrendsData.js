import { useEffect, useMemo, useState } from 'react';

import { getPlayerTrendData } from '../../../../api';
import { PRODUCTION_GROUPS } from '../../../../shared/utils/statMeta';
import { useStatisticsData } from '../../useStatisticsData';
import { DEFAULT_STAT } from '../ChartsMeta';
import { getStatOptions } from '../chartsHelpers';

const playerTrendCache = new Map();
const playerTrendInFlight = new Map();

function getTrendCacheKey(position, playerName, stat) {
  return `${position}:${playerName}:${stat}`;
}

async function fetchPlayerTrendData(playerName, position, stat, key) {
  if (!playerTrendInFlight.has(key)) {
    const request = getPlayerTrendData(playerName, position, stat)
      .then((response) => {
        playerTrendCache.set(key, response.data);
        return response.data;
      })
      .finally(() => {
        playerTrendInFlight.delete(key);
      });
    playerTrendInFlight.set(key, request);
  }

  return playerTrendInFlight.get(key);
}

function getChartGroups(position) {
  const { Rankings: _rankings, ...groups } = PRODUCTION_GROUPS[position] || PRODUCTION_GROUPS.Overall;
  return groups;
}

function getTrendPosition(player) {
  return PRODUCTION_GROUPS[player?.position] ? player.position : 'Overall';
}

export function useSeasonTrendsData({ stat, trendPlayer, enabled = true }) {
  const { statisticsData, loading, error } = useStatisticsData('Overall', null, enabled);
  const [trendData, setTrendData] = useState(null);
  const [trendLoading, setTrendLoading] = useState(Boolean(enabled));
  const [trendError, setTrendError] = useState(null);
  const trendPlayerRecord = useMemo(
    () => statisticsData?.players?.find((player) => player.name === trendPlayer) || null,
    [statisticsData?.players, trendPlayer],
  );
  const trendPosition = getTrendPosition(trendPlayerRecord);
  const statGroups = useMemo(() => getChartGroups(trendPosition), [trendPosition]);
  const statOptions = useMemo(
    () => getStatOptions(statGroups, statisticsData?.stat_columns || []),
    [statGroups, statisticsData?.stat_columns],
  );
  const availableStatOptions = useMemo(() => statOptions.flatMap(({ stats }) => stats), [statOptions]);
  const trendPlayerOptions = useMemo(
    () =>
      (statisticsData?.players || [])
        .map((player) => player.name)
        .filter(Boolean)
        .sort((a, b) => a.localeCompare(b)),
    [statisticsData?.players],
  );

  useEffect(() => {
    let cancelled = false;

    if (!enabled || !stat || !trendPlayer) {
      setTrendData(null);
      setTrendLoading(false);
      setTrendError(null);
      return () => {
        cancelled = true;
      };
    }

    if (loading) {
      setTrendLoading(true);
      return () => {
        cancelled = true;
      };
    }

    if (!trendPlayerRecord) {
      setTrendData(null);
      setTrendLoading(false);
      setTrendError(null);
      return () => {
        cancelled = true;
      };
    }

    const cacheKey = getTrendCacheKey(trendPosition, trendPlayer, stat);
    const cached = playerTrendCache.get(cacheKey);
    if (cached) {
      setTrendData(cached);
      setTrendLoading(false);
      setTrendError(null);
      return () => {
        cancelled = true;
      };
    }

    const loadTrendData = async () => {
      try {
        if (!cancelled) setTrendLoading(true);
        const payload = await fetchPlayerTrendData(trendPlayer, trendPosition, stat, cacheKey);
        if (!cancelled) {
          setTrendData(payload);
          setTrendError(null);
        }
      } catch (err) {
        if (!cancelled) setTrendError(err.message);
      } finally {
        if (!cancelled) setTrendLoading(false);
      }
    };

    loadTrendData();

    return () => {
      cancelled = true;
    };
  }, [enabled, loading, stat, trendPlayer, trendPlayerRecord, trendPosition]);

  return {
    chartData: statisticsData,
    loading,
    error,
    trendLoading,
    trendError,
    statOptions,
    defaultStat: DEFAULT_STAT[trendPosition] || DEFAULT_STAT.Overall,
    availableStatOptions,
    trendPlayerOptions,
    trendSeries: trendData?.points || [],
    chartSeason: statisticsData?.season ?? null,
  };
}

export function __resetSeasonTrendsDataCache() {
  playerTrendCache.clear();
  playerTrendInFlight.clear();
}
