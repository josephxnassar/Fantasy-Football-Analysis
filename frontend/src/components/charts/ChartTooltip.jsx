export default function ChartTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const data = payload[0].payload;

  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-header">
        {data.headshot_url && (
          <img
            src={data.headshot_url}
            alt=""
            className="chart-tooltip-headshot"
            onError={(e) => {
              e.target.src = '/vacant-player.svg';
            }}
          />
        )}
        <div>
          <strong>{data.name}</strong>
          {data.position && <span className="chart-tooltip-team">{data.position}</span>}
          {data.team && <span className="chart-tooltip-team">{data.team}</span>}
        </div>
      </div>
      <div className="chart-tooltip-stats">
        <div>
          {data.statLabel}: <strong>{data.value?.toLocaleString()}</strong>
        </div>
      </div>
    </div>
  );
}
