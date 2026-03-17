// Hook for loading consistency and upside chart payloads.

import { useEffect, useState } from 'react';

import { getConsistencyData } from '../../../api';

const consistencyCache = new Map();
const consistencyInFlight = new Map();

function getCacheKey(position, season, topN) {
  return `${position}:${season ?? 'latest'}:${topN}`;
}

async function fetchConsistencyPayload(position, season, topN, key) {
  if (!consistencyInFlight.has(key)) {
    const request = getConsistencyData(position, season, topN).then((response) => {
        consistencyCache.set(key, response.data);
        return response.data;
      }).finally(() => {consistencyInFlight.delete(key)});
    consistencyInFlight.set(key, request);
  }
  return consistencyInFlight.get(key);
}

export function useConsistencyData(position, season, topN, enabled) {
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

    const cacheKey = getCacheKey(position, season, topN);
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
        const payload = await fetchConsistencyPayload(position, season, topN, cacheKey);
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
  }, [enabled, position, season, topN]);

  return { data, loading, error };
}
