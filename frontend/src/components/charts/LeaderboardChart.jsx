import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import ChartBarShape from './ChartBarShape';
import { getChartHeight } from './chartsHelpers';
import ChartTooltip from './ChartTooltip';

export default function LeaderboardChart({ data, season, onPlayerClick, onPlayerSeasonClick }) {
  const statAxisLabel = data?.[0]?.statLabel || 'Selected Stat';

  const handlePlayerSelection = (playerName) => {
    if (!playerName) return;
    const selectedSeason = Number(season);
    if (onPlayerSeasonClick && Number.isFinite(selectedSeason)) {
      onPlayerSeasonClick(playerName, selectedSeason);
      return;
    }
    onPlayerClick?.(playerName);
  };

  if (!data.length) {
    return (
      <div className="charts-panel charts-panel--leaderboard">
        <p className="charts-no-data">No data available for the selected stat.</p>
      </div>
    );
  }

  const chartHeight = getChartHeight(data.length);

  return (
    <div className="charts-panel charts-panel--leaderboard chart-wrapper">
      {/* Height scales with row count so labels remain readable. */}
      <ResponsiveContainer width="100%" height={chartHeight}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 10, right: 40, bottom: 34, left: 18 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" horizontal={false} />
          <XAxis
            type="number"
            tick={{ fontSize: 12 }}
            stroke="var(--color-text-muted)"
            label={{ value: statAxisLabel, position: 'insideBottom', offset: -8 }}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={150}
            tick={{ fontSize: 12, cursor: 'pointer' }}
            stroke="var(--color-text-muted)"
            label={{ value: 'Player', angle: -90, position: 'insideLeft' }}
            onClick={(e) => {
              // Clicking a player label opens the player modal.
              if (e?.value) handlePlayerSelection(e.value);
            }}
          />
          <Tooltip cursor={false} content={<ChartTooltip />} />
          <Bar
            dataKey="value"
            shape={(shapeProps) => (
              <ChartBarShape {...shapeProps} onBarClick={handlePlayerSelection} />
            )}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
