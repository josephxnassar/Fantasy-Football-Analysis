/* Bar chart tab — single-stat horizontal bar chart with position/season controls. */

import { useEffect, useMemo, useState } from 'react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { useChartData } from '../hooks/useChartData';
import { usePlayerDetails } from '../hooks/usePlayerDetails';
import { POSITION_STAT_GROUPS } from '../utils/statDefinitions';
import { ErrorMessage, LoadingMessage } from './common';
import ChartBarShape from './charts/ChartBarShape';
import ChartControls from './charts/ChartControls';
import { buildBarData, DEFAULT_STAT, getChartHeight, getStatOptions } from './charts/chartsHelpers';
import ChartTooltip from './charts/ChartTooltip';
import PlayerDetailsModal from './PlayerDetailsModal';
import './Charts.css';

export default function Charts() {
  // UI controls for the chart query.
  const [position, setPosition] = useState('Overall');
  const [season, setSeason] = useState(null);
  const [stat, setStat] = useState(DEFAULT_STAT.Overall);
  const [topN, setTopN] = useState(20);

  // Server payload for selected position + season.
  const { chartData, loading, error } = useChartData(position, season);

  // Shared player-modal state/handlers reused from search/chart clicks.
  const {
    playerDetails,
    loadingDetails,
    availableSeasons: playerSeasons,
    currentSeason: playerSeason,
    handlePlayerClick,
    handleSeasonChange: handlePlayerSeasonChange,
    closeDetails,
  } = usePlayerDetails();

  // Flatten API rows into sorted chart bars for the selected stat.
  const barData = useMemo(() => buildBarData(chartData?.players, stat, topN), [chartData?.players, stat, topN]);

  // Build grouped stat picker options from available columns + position config.
  const statOptions = useMemo(
    () => getStatOptions(position, chartData?.stat_columns || [], POSITION_STAT_GROUPS),
    [position, chartData?.stat_columns]
  );

  useEffect(() => {
    // Keep selected stat valid when position/season payload changes.
    const filteredStats = statOptions.flatMap(({ stats }) => stats);
    if (!filteredStats.length) return;
    if (!filteredStats.includes(stat)) {
      setStat(filteredStats[0]);
    }
  }, [statOptions, stat]);

  const chartHeight = getChartHeight(barData.length);

  if (loading) return <LoadingMessage message="Loading chart data..." />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="charts-container">
      <h1>Stat Charts</h1>

      <ChartControls
        position={position}
        setPosition={setPosition}
        chartData={chartData}
        season={season}
        setSeason={setSeason}
        stat={stat}
        setStat={setStat}
        statOptions={statOptions}
        topN={topN}
        setTopN={setTopN}
      />

      {barData.length === 0 ? (
        <p className="charts-no-data">No data available for the selected stat.</p>
      ) : (
        <div className="chart-wrapper">
          {/* Height scales with row count so labels remain readable. */}
          <ResponsiveContainer width="100%" height={chartHeight}>
            <BarChart
              data={barData}
              layout="vertical"
              margin={{ top: 10, right: 40, bottom: 10, left: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" horizontal={false} />
              <XAxis
                type="number"
                tick={{ fontSize: 12 }}
                stroke="var(--color-text-muted)"
              />
              <YAxis
                type="category"
                dataKey="name"
                width={150}
                tick={{ fontSize: 12, cursor: 'pointer' }}
                stroke="var(--color-text-muted)"
                onClick={(e) => {
                  // Clicking a player label opens the player modal.
                  if (e?.value) handlePlayerClick(e.value);
                }}
              />
              <Tooltip cursor={false} content={<ChartTooltip />} />
              <Bar
                dataKey="value"
                shape={(shapeProps) => (
                  <ChartBarShape {...shapeProps} onBarClick={handlePlayerClick} />
                )}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {(playerDetails || loadingDetails) && (
        <PlayerDetailsModal
          playerDetails={playerDetails}
          loading={loadingDetails}
          onClose={closeDetails}
          availableSeasons={playerSeasons}
          currentSeason={playerSeason}
          onSeasonChange={handlePlayerSeasonChange}
        />
      )}
    </div>
  );
}
