import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

export default function SeasonTrendsChart({ data, playerName, statLabel, onPlayerClick, onPlayerSeasonClick }) {
  if (!playerName || !data.length) {
    return <p className="charts-no-data">No multi-season trend data available for this selection.</p>;
  }

  const hasPointClickAction = Boolean(onPlayerSeasonClick || onPlayerClick);
  const handleTrendPointClick = (payload) => {
    const clickedSeason = Number(payload?.season);
    if (onPlayerSeasonClick && Number.isFinite(clickedSeason)) {
      onPlayerSeasonClick(playerName, clickedSeason);
      return;
    }

    onPlayerClick?.(playerName);
  };
  const renderDot = (dotProps) => {
    const { cx, cy, payload } = dotProps;
    if (cx == null || cy == null) return null;

    return (
      <circle
        cx={cx}
        cy={cy}
        r={3}
        fill="#4f6ee4"
        stroke="#4f6ee4"
        cursor={hasPointClickAction ? 'pointer' : 'default'}
        onClick={() => handleTrendPointClick(payload)}
      />
    );
  };
  const renderActiveDot = (dotProps) => {
    const { cx, cy, payload } = dotProps;
    if (cx == null || cy == null) return null;

    return (
      <circle
        cx={cx}
        cy={cy}
        r={5}
        fill="#4f6ee4"
        stroke="#4f6ee4"
        cursor={hasPointClickAction ? 'pointer' : 'default'}
        onClick={() => handleTrendPointClick(payload)}
      />
    );
  };

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
            dot={renderDot}
            activeDot={renderActiveDot}
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
