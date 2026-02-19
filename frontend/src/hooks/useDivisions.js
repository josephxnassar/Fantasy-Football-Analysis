/* Hook for loading and caching divisions data. Prevents duplicate API calls when multiple components need division data. */

import { useState, useEffect, useMemo } from 'react';
import { getDivisions } from '../api';

let cachedDivisionPayload = null;
let divisionsRequestPromise = null;

export function useDivisions() {
  const [divisions, setDivisions] = useState(null);
  const [teamNames, setTeamNames] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    if (cachedDivisionPayload) {
      if (!cancelled) {
        setDivisions(cachedDivisionPayload.divisions);
        setTeamNames(cachedDivisionPayload.team_names);
        setLoading(false);
        setError(null);
      }
      return () => {
        cancelled = true;
      };
    }

    const fetchDivisions = async () => {
      try {
        if (!cancelled) {
          setLoading(true);
        }
        if (!divisionsRequestPromise) {
          divisionsRequestPromise = getDivisions();
        }
        const response = await divisionsRequestPromise;
        cachedDivisionPayload = response.data;
        if (!cancelled) {
          setDivisions(response.data.divisions);
          setTeamNames(response.data.team_names);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError('Failed to load division data');
        }
        console.error(err);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
        divisionsRequestPromise = null;
      }
    };

    fetchDivisions();

    return () => {
      cancelled = true;
    };
  }, []);

  const allTeams = useMemo(
    () =>
      divisions
        ? Object.values(divisions)
            .flatMap((conference) => Object.values(conference).flat())
            .sort()
        : [],
    [divisions]
  );

  return { divisions, teamNames, allTeams, loading, error };
}
