// Hook for loading consistency and upside chart payloads.

import { useEffect, useState } from 'react';

import { getConsistencyData } from '../../../api';
import { PLAYER_DISPLAY_LIMIT } from '../statisticsOptions';

const consistencyCache = new Map();
const consistencyInFlight = new Map();

function getCacheKey(position, season) {
  return `${position}:${season ?? 'latest'}`;
}

async function fetchConsistencyPayload(position, season, key) {
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

export function useConsistencyData(position, season, enabled) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(Boolean(enabled));
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    if (!enabled) {
      setLoading(false);
      setError(null);
      return () => {
        cancelled = true;
      };
    }

    const cacheKey = getCacheKey(position, season);
    const cached = consistencyCache.get(cacheKey);
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
        const payload = await fetchConsistencyPayload(position, season, cacheKey);
        if (!cancelled) {
          setData(payload);
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
  }, [enabled, position, season]);

  return { data, loading, error };
}
