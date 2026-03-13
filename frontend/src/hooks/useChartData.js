// Hook for loading chart payloads by position and season.

import { useEffect, useState } from 'react';
import { getChartData } from '../api';

const chartDataCache = new Map();
const chartDataInFlight = new Map();

function getCacheKey(position, season) {
  return `${position}:${season ?? 'latest'}`;
}

async function fetchChartPayload(position, season, key) {
  if (!chartDataInFlight.has(key)) {
    const request = getChartData(position, season)
      .then((response) => {
        chartDataCache.set(key, response.data);
        return response.data;
      })
      .finally(() => {
        chartDataInFlight.delete(key);
      });
    chartDataInFlight.set(key, request);
  }
  return chartDataInFlight.get(key);
}

export function useChartData(position, season) {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const cacheKey = getCacheKey(position, season);
    const cached = chartDataCache.get(cacheKey);
    if (cached) {
      setChartData(cached);
      setLoading(false);
      setError(null);
      return () => {
        cancelled = true;
      };
    }

    const fetchData = async () => {
      // Pull chart payload for current position + season filter.
      try {
        if (!cancelled) setLoading(true);
        const payload = await fetchChartPayload(position, season, cacheKey);
        if (!cancelled) {
          setChartData(payload);
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
  }, [position, season]);

  return { chartData, loading, error };
}

export function __resetChartDataCache() {
  chartDataCache.clear();
  chartDataInFlight.clear();
}
