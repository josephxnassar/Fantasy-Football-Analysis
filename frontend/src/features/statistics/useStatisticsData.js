import { useEffect, useState } from 'react';

import { getChartData } from '../../api';

const statisticsDataCache = new Map();
const statisticsDataInFlight = new Map();

function getCacheKey(position, season) {
  return `${position}:${season ?? 'latest'}`;
}

async function fetchStatisticsPayload(position, season, key) {
  if (!statisticsDataInFlight.has(key)) {
    const request = getChartData(position, season)
      .then((response) => {
        statisticsDataCache.set(key, response.data);
        return response.data;
      })
      .finally(() => {
        statisticsDataInFlight.delete(key);
      });
    statisticsDataInFlight.set(key, request);
  }

  return statisticsDataInFlight.get(key);
}

export function useStatisticsData(position, season, enabled = true) {
  const cacheKey = getCacheKey(position, season);
  const [statisticsData, setStatisticsData] = useState(null);
  const [loading, setLoading] = useState(Boolean(enabled));
  const [error, setError] = useState(null);
  const cachedData = enabled ? statisticsDataCache.get(cacheKey) || null : null;
  const resolvedStatisticsData = statisticsData ?? cachedData;
  const resolvedLoading = enabled && (loading || (resolvedStatisticsData === null && error === null));

  useEffect(() => {
    let cancelled = false;

    if (!enabled) {
      setStatisticsData(null);
      setLoading(false);
      setError(null);
      return () => {
        cancelled = true;
      };
    }

    const cached = statisticsDataCache.get(cacheKey);
    if (cached) {
      setStatisticsData(cached);
      setLoading(false);
      setError(null);
      return () => {
        cancelled = true;
      };
    }

    const fetchData = async () => {
      try {
        if (!cancelled) setLoading(true);
        const payload = await fetchStatisticsPayload(position, season, cacheKey);
        if (!cancelled) {
          setStatisticsData(payload);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [cacheKey, enabled, position, season]);

  return { statisticsData: resolvedStatisticsData, loading: resolvedLoading, error };
}

export function __resetStatisticsDataCache() {
  statisticsDataCache.clear();
  statisticsDataInFlight.clear();
}
