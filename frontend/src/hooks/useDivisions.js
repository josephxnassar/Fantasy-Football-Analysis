/* Hook for loading and caching divisions data. Prevents duplicate API calls when multiple components need division data. */

import { useState, useEffect } from 'react';
import { getDivisions } from '../api';

export function useDivisions() {
  const [divisions, setDivisions] = useState(null);
  const [teamNames, setTeamNames] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDivisions = async () => {
      try {
        setLoading(true);
        const response = await getDivisions();
        setDivisions(response.data.divisions);
        setTeamNames(response.data.team_names);
        setError(null);
      } catch (err) {
        setError('Failed to load division data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDivisions();
  }, []);

  // Derive flattened teams list for search functionality
  const allTeams = divisions
    ? Object.values(divisions)
        .flatMap(conference => Object.values(conference).flat())
        .sort()
    : [];

  return { divisions, teamNames, allTeams, loading, error };
}
