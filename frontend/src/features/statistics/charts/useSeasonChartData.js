// Hook for loading single-player season trend points.

import { useEffect, useState } from 'react';

import { getPlayerTrendData } from '../../../api';

const seasonChartCache = new Map();
const seasonChartInFlight = new Map();

function getCacheKey(position, playerName, stat) {
  return `${position}:${playerName}:${stat}`;
}

async function fetchPlayerTrendPayload(playerName, position, stat, key) {
  if (!seasonChartInFlight.has(key)) {
    const request = getPlayerTrendData(playerName, position, stat).then((response) => {
        seasonChartCache.set(key, response.data);
        return response.data;
      }).finally(() => {seasonChartInFlight.delete(key)});
    seasonChartInFlight.set(key, request);
  }

  return seasonChartInFlight.get(key);
}

export function useSeasonChartData(position, playerName, stat, enabled) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(Boolean(enabled));
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    if (!enabled || !playerName || !stat) {
      setData(null);
      setLoading(false);
      setError(null);
      return () => {
        cancelled = true;
      };
    }

    const cacheKey = getCacheKey(position, playerName, stat);
    const cached = seasonChartCache.get(cacheKey);
    if (cached) {
      setData(cached);
      setLoading(false);
      setError(null);
      return () => {
        cancelled = true;
      };
    }

    const fetchData = async () => {
      try {
        if (!cancelled) setLoading(true);
        const payload = await fetchPlayerTrendPayload(playerName, position, stat, cacheKey);
        if (!cancelled) {
          setData(payload);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) 
          setError(err.message);
      } finally {
        if (!cancelled) 
          setLoading(false);
      }
    };

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [enabled, playerName, position, stat]);

  return { data, loading, error };
}

export function __resetSeasonChartDataCache() {
  seasonChartCache.clear();
  seasonChartInFlight.clear();
}
