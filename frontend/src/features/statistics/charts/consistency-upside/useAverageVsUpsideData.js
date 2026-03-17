import { useEffect, useState } from 'react';

import { getConsistencyData } from '../../../../api';
import { useStatisticsData } from '../../useStatisticsData';
import { PLAYER_DISPLAY_LIMIT } from '../../statisticsOptions';

const consistencyCache = new Map();
const consistencyInFlight = new Map();

function getCacheKey(position, season) {
  return `${position}:${season ?? 'latest'}`;
}

async function fetchConsistencyData(position, season, key) {
  if (!consistencyInFlight.has(key)) {
    const request = getConsistencyData(position, season, PLAYER_DISPLAY_LIMIT)
      .then((response) => {
        consistencyCache.set(key, response.data);
        return response.data;
      })
      .finally(() => {
        consistencyInFlight.delete(key);
      });
    consistencyInFlight.set(key, request);
  }

  return consistencyInFlight.get(key);
}

export function useAverageVsUpsideData({ position, season, enabled = true }) {
  const { statisticsData, loading, error } = useStatisticsData(position, season, enabled);
  const [consistencyData, setConsistencyData] = useState(null);
  const [consistencyLoading, setConsistencyLoading] = useState(Boolean(enabled));
  const [consistencyError, setConsistencyError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    if (!enabled) {
      setConsistencyData(null);
      setConsistencyLoading(false);
      setConsistencyError(null);
      return () => {
        cancelled = true;
      };
    }

    const cacheKey = getCacheKey(position, season);
    const cached = consistencyCache.get(cacheKey);
    if (cached) {
      setConsistencyData(cached);
      setConsistencyLoading(false);
      setConsistencyError(null);
      return () => {
        cancelled = true;
      };
    }

    const loadConsistencyData = async () => {
      try {
        if (!cancelled) setConsistencyLoading(true);
        const payload = await fetchConsistencyData(position, season, cacheKey);
        if (!cancelled) {
          setConsistencyData(payload);
          setConsistencyError(null);
        }
      } catch (err) {
        if (!cancelled) setConsistencyError(err.message);
      } finally {
        if (!cancelled) setConsistencyLoading(false);
      }
    };

    loadConsistencyData();

    return () => {
      cancelled = true;
    };
  }, [enabled, position, season]);

  return {
    chartData: statisticsData,
    loading,
    error,
    consistencyData,
    consistencyLoading,
    consistencyError,
    chartSeason: season ?? statisticsData?.season ?? null,
  };
}

export function __resetAverageVsUpsideDataCache() {
  consistencyCache.clear();
  consistencyInFlight.clear();
}
