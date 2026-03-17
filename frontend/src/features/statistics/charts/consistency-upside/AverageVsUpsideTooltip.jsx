export default function AverageVsUpsideTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;

  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-header">
        <div>
          <strong>{point.name}</strong>
          {point.position && <span className="chart-tooltip-team">{point.position}</span>}
          {point.team && <span className="chart-tooltip-team">{point.team}</span>}
        </div>
      </div>
      <div className="chart-tooltip-stats">
        <div>
          Weekly Avg PPR: <strong>{point.avg_fp_ppr.toFixed(2)}</strong>
        </div>
        <div>
          Weekly Ceiling PPR: <strong>{point.ceiling_fp_ppr.toFixed(2)}</strong>
        </div>
        <div>
          Volatility (Std Dev): <strong>{point.volatility_fp_ppr.toFixed(2)}</strong>
        </div>
        <div>
          Games: <strong>{point.games}</strong>
        </div>
      </div>
    </div>
  );
}
