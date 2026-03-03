/* Hook for loading application overview metadata from /api/app-info */

import { useState, useEffect } from 'react';
import { getAppInfo } from '../api';

let cachedAppInfo = null;

export function useAppInfo() {
  const [data, setData] = useState(cachedAppInfo);
  const [loading, setLoading] = useState(!cachedAppInfo);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (cachedAppInfo) return;

    let cancelled = false;
    const fetchInfo = async () => {
      try {
        const response = await getAppInfo();
        cachedAppInfo = response.data;
        if (!cancelled) {
          setData(response.data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError('Failed to load app info');
        }
        console.error(err);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };
    fetchInfo();
    return () => { cancelled = true; };
  }, []);

  return { data, loading, error };
}
