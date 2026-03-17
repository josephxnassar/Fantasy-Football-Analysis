import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { StatTooltip } from '../../../shared/ui';
import { formatStatForDisplay, getStatDefinition } from '../../../shared/utils/statDefinitions';
import ChartBarShape from './ChartBarShape';
import { getChartHeight } from './chartsHelpers';
import ChartTooltip from './ChartTooltip';

export default function LeaderboardChart({ data, stat, season, onPlayerClick, onPlayerSeasonClick }) {
  const statAxisLabel = data?.[0]?.statLabel || 'Selected Stat';
  const statDescription = getStatDefinition(stat);

  const handlePlayerSelection = (playerName) => {
    if (!playerName)
      return;
    const selectedSeason = Number(season);
    if (onPlayerSeasonClick && Number.isFinite(selectedSeason)) {
      onPlayerSeasonClick(playerName, selectedSeason);
      return;
    }
    onPlayerClick?.(playerName);
  };

  if (!data.length)
    return (
      <div className="charts-panel charts-panel--leaderboard">
        <p className="charts-no-data">No data available for the selected stat.</p>
      </div>
    );

  const chartHeight = getChartHeight(data.length);

  return (
    <div className="charts-panel charts-panel--leaderboard chart-wrapper">
      <ResponsiveContainer width="100%" height={chartHeight}>
        <BarChart data={data} layout="vertical" margin={{ top: 10, right: 40, bottom: 20, left: 18 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" horizontal={false}/>
          <XAxis type="number" tick={{ fontSize: 12 }} stroke="var(--color-text-muted)" tickFormatter={(value) => formatStatForDisplay(stat, value)}/>
          <YAxis type="category" dataKey="name" width={150} tick={{ fontSize: 12, cursor: 'pointer' }} stroke="var(--color-text-muted)" label={{ value: 'Player', angle: -90, position: 'insideLeft' }} onClick={(e) => {
            if (e?.value)
              handlePlayerSelection(e.value);
          }}/>
          <Tooltip cursor={false} content={<ChartTooltip />} />
          <Bar dataKey="value" shape={(shapeProps) => (<ChartBarShape {...shapeProps} onBarClick={handlePlayerSelection} />)}/>
        </BarChart>
      </ResponsiveContainer>
      <div className="chart-axis-meta">
        <span className="chart-axis-meta__label">{statAxisLabel}</span>
        <StatTooltip label={statAxisLabel} description={statDescription}/>
      </div>
    </div>
  );
}
