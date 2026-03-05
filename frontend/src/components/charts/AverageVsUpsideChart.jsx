import { ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis } from 'recharts';

export default function AverageVsUpsideChart({ data, onPlayerClick }) {
  if (!data.length) {
    return <p className="charts-no-data">No weekly data available for this season.</p>;
  }

  return (
    <div className="charts-panel chart-wrapper">
      <ResponsiveContainer width="100%" height={420}>
        <ScatterChart margin={{ top: 12, right: 22, bottom: 22, left: 8 }}>
          <XAxis
            type="number"
            dataKey="avg_fp_ppr"
            name="Weekly Avg PPR"
            stroke="var(--color-text-muted)"
            tick={{ fontSize: 12 }}
          />
          <YAxis
            type="number"
            dataKey="ceiling_fp_ppr"
            name="Weekly Ceiling PPR"
            stroke="var(--color-text-muted)"
            tick={{ fontSize: 12 }}
          />
          <ZAxis type="number" dataKey="games" range={[48, 260]} />
          <Tooltip
            cursor={false}
            content={({ active, payload }) => {
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
                    <div>Weekly Avg PPR: <strong>{point.avg_fp_ppr.toFixed(2)}</strong></div>
                    <div>Weekly Ceiling PPR: <strong>{point.ceiling_fp_ppr.toFixed(2)}</strong></div>
                    <div>Volatility (Std Dev): <strong>{point.volatility_fp_ppr.toFixed(2)}</strong></div>
                    <div>Games: <strong>{point.games}</strong></div>
                  </div>
                </div>
              );
            }}
          />
          <Scatter
            data={data}
            fill="#3c90d4"
            onClick={(point) => {
              const playerName = point?.payload?.name || point?.name;
              if (playerName) onPlayerClick?.(playerName);
            }}
          />
        </ScatterChart>
      </ResponsiveContainer>
      <p className="charts-trend-caption">Bubble size = games played.</p>
    </div>
  );
}
