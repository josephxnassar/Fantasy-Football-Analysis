import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { formatStatForDisplay } from '../../../../shared/utils/statDefinitions';
import SeasonTrendsTooltip from './SeasonTrendsTooltip';

export default function SeasonTrendsChart({ data, playerName, stat, statLabel, onPlayerClick, onPlayerSeasonClick }) {
  if (!playerName || !data.length) return <p className="charts-no-data">No multi-season trend data available for this selection.</p>;

  const hasPointClickAction = Boolean(onPlayerSeasonClick || onPlayerClick);
  const trendColor = 'var(--color-primary)';
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
        fill={trendColor}
        stroke={trendColor}
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
        fill={trendColor}
        stroke={trendColor}
        cursor={hasPointClickAction ? 'pointer' : 'default'}
        onClick={() => handleTrendPointClick(payload)}
      />
    );
  };

  return (
    <div className="charts-panel chart-wrapper">
      <ResponsiveContainer width="100%" height={430}>
        <LineChart data={data} margin={{ top: 12, right: 32, bottom: 34, left: 16 }}>
          <XAxis
            dataKey="season"
            stroke="var(--color-text-muted)"
            tick={{ fontSize: 12 }}
            label={{ value: 'Season', position: 'insideBottom', offset: -8 }}
          />
          <YAxis
            stroke="var(--color-text-muted)"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => formatStatForDisplay(stat, value)}
            label={{ value: statLabel, angle: -90, position: 'insideLeft' }}
          />
          <Tooltip cursor={false} content={<SeasonTrendsTooltip playerName={playerName} stat={stat} statLabel={statLabel} />} />
          <Line
            type="monotone"
            dataKey="value"
            name={playerName}
            connectNulls
            stroke={trendColor}
            strokeWidth={2.8}
            dot={renderDot}
            activeDot={renderActiveDot}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="charts-trend-caption">
        Showing {statLabel} across seasons for{' '}
        <button type="button" className="charts-player-link" onClick={() => onPlayerClick?.(playerName)}>
          {playerName}
        </button>
        .
      </p>
    </div>
  );
}
