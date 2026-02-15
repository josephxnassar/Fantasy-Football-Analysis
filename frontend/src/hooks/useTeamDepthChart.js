/* Hook for loading team depth chart data by team abbreviation. */

import { useEffect, useState } from 'react';
import { getTeamDepthChart } from '../api';

export function useTeamDepthChart(team) {
  const [teamDepthChart, setTeamDepthChart] = useState(null);
  const [depthChartLoading, setDepthChartLoading] = useState(false);

  useEffect(() => {
    if (!team) {
      setTeamDepthChart(null);
      setDepthChartLoading(false);
      return;
    }

    const fetchDepthChart = async () => {
      try {
        setDepthChartLoading(true);
        const response = await getTeamDepthChart(team);
        setTeamDepthChart(response.data);
      } catch (err) {
        console.error(`Failed to load depth chart: ${err.message}`);
        setTeamDepthChart(null);
      } finally {
        setDepthChartLoading(false);
      }
    };

    fetchDepthChart();
  }, [team]);

  return { teamDepthChart, depthChartLoading };
}
