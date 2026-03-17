import { formatStatForDisplay } from '../../../../shared/utils/statDefinitions';

export default function SeasonTrendsTooltip({ active, label, payload, playerName, stat, statLabel }) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;

  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-header">
        <div>
          <strong>{playerName}</strong>
          <span className="chart-tooltip-team">{label} Season</span>
        </div>
      </div>
      <div className="chart-tooltip-stats">
        <div>
          {statLabel}: <strong>{formatStatForDisplay(stat, point.value)}</strong>
        </div>
      </div>
    </div>
  );
}
