/* Shared hook for team-based modal data loading. */

import { useEffect, useState } from 'react';

export function useTeamModalData(team, fetchFn, defaultErrorMessage) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTeamData = async () => {
      if (!team) {
        setData(null);
        setError(null);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await fetchFn(team);
        setData(response.data);
        setError(null);
      } catch (err) {
        setError(defaultErrorMessage);
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTeamData();
  }, [team, fetchFn, defaultErrorMessage]);

  return { data, loading, error };
}
