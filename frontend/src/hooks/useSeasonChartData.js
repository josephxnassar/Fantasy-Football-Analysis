/* Hook for loading all seasonal chart payloads for trend visualizations. */

import { useEffect, useState } from 'react';

import { getChartData } from '../api';

const seasonChartCache = new Map();
const seasonChartInFlight = new Map();

async function fetchAllSeasonPayloads(position) {
  if (!seasonChartInFlight.has(position)) {
    const request = (async () => {
      const latestResponse = await getChartData(position, null);
      const latest = latestResponse.data;
      const availableSeasons = latest.available_seasons || [latest.season];
      const payloadsBySeason = new Map([[latest.season, latest]]);

      const missingSeasonRequests = availableSeasons
        .filter((season) => season !== latest.season)
        .map(async (season) => {
          const response = await getChartData(position, season);
          return response.data;
        });

      const missingPayloads = await Promise.all(missingSeasonRequests);
      missingPayloads.forEach((payload) => {
        payloadsBySeason.set(payload.season, payload);
      });

      const payload = {
        seasons: availableSeasons,
        season_payloads: availableSeasons
          .map((season) => payloadsBySeason.get(season))
          .filter(Boolean),
      };
      seasonChartCache.set(position, payload);
      return payload;
    })().finally(() => {
      seasonChartInFlight.delete(position);
    });

    seasonChartInFlight.set(position, request);
  }

  return seasonChartInFlight.get(position);
}

export function useSeasonChartData(position, enabled) {
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

    const cached = seasonChartCache.get(position);
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
        const payload = await fetchAllSeasonPayloads(position);
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
  }, [enabled, position]);

  return { data, loading, error };
}
