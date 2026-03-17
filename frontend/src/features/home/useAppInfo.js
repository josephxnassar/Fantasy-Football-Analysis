// Hook for loading application overview metadata from /api/app-info.

import { useState, useEffect } from 'react';
import { getAppInfo } from '../../api';

let cachedAppInfo = null;
let appInfoRequestPromise = null;

export function useAppInfo() {
  const [data, setData] = useState(cachedAppInfo);
  const [loading, setLoading] = useState(!cachedAppInfo);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    if (cachedAppInfo) {
      setData(cachedAppInfo);
      setError(null);
      setLoading(false);
      return () => {
        cancelled = true;
      };
    }

    const fetchInfo = async () => {
      try {
        if (!cancelled) {
          setLoading(true);
        }
        if (!appInfoRequestPromise) {
          appInfoRequestPromise = getAppInfo();
        }
        const response = await appInfoRequestPromise;
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
        appInfoRequestPromise = null;
      }
    };
    
    fetchInfo();
    return () => { cancelled = true; };
  }, []);

  return { data, loading, error };
}
