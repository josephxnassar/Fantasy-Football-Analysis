import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

export default function SeasonTrendsChart({ data, playerName, statLabel, onPlayerClick }) {
  if (!playerName || !data.length) {
    return <p className="charts-no-data">No multi-season trend data available for this selection.</p>;
  }

  return (
    <div className="charts-panel chart-wrapper">
      <ResponsiveContainer width="100%" height={430}>
        <LineChart data={data} margin={{ top: 12, right: 32, bottom: 12, left: 8 }}>
          <XAxis dataKey="season" stroke="var(--color-text-muted)" tick={{ fontSize: 12 }} />
          <YAxis stroke="var(--color-text-muted)" tick={{ fontSize: 12 }} />
          <Tooltip
            cursor={false}
            formatter={(value) => [value?.toLocaleString(), statLabel]}
            labelFormatter={(season) => `${season} Season`}
          />
          <Line
            type="monotone"
            dataKey="value"
            name={playerName}
            connectNulls
            stroke="#4f6ee4"
            strokeWidth={2.8}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="charts-trend-caption">
        Showing {statLabel} across seasons for{' '}
        <button
          type="button"
          className="charts-player-link"
          onClick={() => onPlayerClick?.(playerName)}
        >
          {playerName}
        </button>
        .
      </p>
    </div>
  );
}
