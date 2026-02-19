/* Shared hook for team-based modal data loading. */

import { useEffect, useState } from 'react';

export function useTeamModalData(team, fetchFn, defaultErrorMessage) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const fetchTeamData = async () => {
      if (!team) {
        if (!cancelled) {
          setData(null);
          setError(null);
          setLoading(false);
        }
        return;
      }

      try {
        if (!cancelled) {
          setLoading(true);
        }
        const response = await fetchFn(team);
        if (!cancelled) {
          setData(response.data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(defaultErrorMessage);
        }
        console.error(err);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchTeamData();

    return () => {
      cancelled = true;
    };
  }, [team, fetchFn, defaultErrorMessage]);

  return { data, loading, error };
}
