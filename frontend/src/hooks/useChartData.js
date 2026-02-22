/* Hook for loading chart payloads by position/season. */

import { useCallback, useEffect, useState } from 'react';
import { getChartData } from '../api';

export function useChartData(position, season) {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getChartData(position, season);
      setChartData(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [position, season]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { chartData, loading, error };
}
