import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import ChartBarShape from './ChartBarShape';
import { getChartHeight } from './chartsHelpers';
import ChartTooltip from './ChartTooltip';

export default function LeaderboardChart({ data, onPlayerClick }) {
  if (!data.length) {
    return (
      <div className="charts-panel">
        <p className="charts-no-data">No data available for the selected stat.</p>
      </div>
    );
  }

  const chartHeight = getChartHeight(data.length);

  return (
    <div className="charts-panel chart-wrapper">
      {/* Height scales with row count so labels remain readable. */}
      <ResponsiveContainer width="100%" height={chartHeight}>
        <BarChart
          data={data}
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
              if (e?.value) onPlayerClick(e.value);
            }}
          />
          <Tooltip cursor={false} content={<ChartTooltip />} />
          <Bar
            dataKey="value"
            shape={(shapeProps) => (
              <ChartBarShape {...shapeProps} onBarClick={onPlayerClick} />
            )}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
