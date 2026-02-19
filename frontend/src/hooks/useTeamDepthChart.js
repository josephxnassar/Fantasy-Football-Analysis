/* Hook for loading team depth chart data by team abbreviation. */

import { useEffect, useState } from 'react';
import { getTeamDepthChart } from '../api';

export function useTeamDepthChart(team) {
  const [teamDepthChart, setTeamDepthChart] = useState(null);
  const [depthChartLoading, setDepthChartLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;

    if (!team) {
      if (!cancelled) {
        setTeamDepthChart(null);
        setDepthChartLoading(false);
      }
      return;
    }

    const fetchDepthChart = async () => {
      try {
        if (!cancelled) {
          setDepthChartLoading(true);
        }
        const response = await getTeamDepthChart(team);
        if (!cancelled) {
          setTeamDepthChart(response.data);
        }
      } catch (err) {
        console.error(`Failed to load depth chart: ${err.message}`);
        if (!cancelled) {
          setTeamDepthChart(null);
        }
      } finally {
        if (!cancelled) {
          setDepthChartLoading(false);
        }
      }
    };

    fetchDepthChart();

    return () => {
      cancelled = true;
    };
  }, [team]);

  return { teamDepthChart, depthChartLoading };
}
