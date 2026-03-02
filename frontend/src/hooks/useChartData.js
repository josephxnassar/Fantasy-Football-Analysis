/* Hook for loading chart payloads by position/season. */

import { useEffect, useState } from 'react';
import { getChartData } from '../api';

export function useChartData(position, season) {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      // Pull chart payload for current position + season filter.
      try {
        if (!cancelled) setLoading(true);
        const response = await getChartData(position, season);
        if (!cancelled) {
          setChartData(response.data);
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
