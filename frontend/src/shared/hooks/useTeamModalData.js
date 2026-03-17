/**
 * File overview: Shared hook for team-based modal fetches with stale-request protection.
 */

import { useEffect, useState } from 'react';

export function useTeamModalData(team, fetchFn, defaultErrorMessage) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Team modals can switch quickly between teams or tabs, so ignore any late
    // response once the current effect has been replaced.
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
          setData(null);
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
