/* Bar chart tab — single-stat horizontal bar chart with position/season controls. Bars are clickable (opens player modal) and show tooltip on hover. */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip, Rectangle } from 'recharts';
import { getChartData } from '../api';
import { POSITION_STAT_GROUPS } from '../utils/statDefinitions';
import { TOP_N_OPTIONS } from '../utils/uiOptions';
import { usePlayerDetails } from '../hooks/usePlayerDetails';
import PlayerDetailsModal from './PlayerDetailsModal';
import { LoadingMessage, ErrorMessage } from './common';
import './Charts.css';

/** Default stat per position */
const DEFAULT_STAT = {
  QB: 'Pass Yds',
  RB: 'Rush Yds',
  WR: 'Rec Yds',
  TE: 'Rec Yds',
  Overall: 'PPR Pts',
};

const DERIVED_STAT_THRESHOLDS = {
  'Yds/Rush': { volumeStat: 'Carries', minVolume: 100 },
  'Yds/Rec': { volumeStat: 'Rec', minVolume: 50 },
};

/** Build grouped options from POSITION_STAT_GROUPS */
function getStatOptions(position, statColumns = []) {
  const groups = POSITION_STAT_GROUPS[position];
  if (!groups) return [];
  return Object.entries(groups)
    .map(([category, stats]) => ({
      category,
      stats: stats.filter((s) => statColumns.includes(s)),
    }))
    .filter(({ stats }) => stats.length > 0);
}

function meetsDerivedThreshold(player, stat) {
  const threshold = DERIVED_STAT_THRESHOLDS[stat];
  if (!threshold) return true;
  const volume = player?.stats?.[threshold.volumeStat];
  return typeof volume === 'number' && volume >= threshold.minVolume;
}

/** Custom tooltip content with headshot */
function CustomTooltip({ active, payload }) {
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
            onError={(e) => { e.target.src = '/vacant-player.svg'; }}
          />
        )}
        <div>
          <strong>{data.name}</strong>
          {data.position && <span className="chart-tooltip-team">{data.position}</span>}
          {data.team && <span className="chart-tooltip-team">{data.team}</span>}
        </div>
      </div>
      <div className="chart-tooltip-stats">
        <div>{data.statLabel}: <strong>{data.value?.toLocaleString()}</strong></div>
      </div>
    </div>
  );
}

function CustomBarShape(props) {
  const { index, payload, onBarClick, ...rectProps } = props;
  const fill = `hsl(225, 73%, ${Math.max(40, 65 - index * 0.8)}%)`;

  return (
    <Rectangle
      {...rectProps}
      fill={fill}
      radius={[0, 4, 4, 0]}
      cursor="pointer"
      onClick={() => {
        if (payload?.name) onBarClick(payload.name);
      }}
    />
  );
}

export default function Charts() {
  const [position, setPosition] = useState('Overall');
  const [season, setSeason] = useState(null);
  const [stat, setStat] = useState(DEFAULT_STAT.Overall);
  const [topN, setTopN] = useState(20);
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const {
    playerDetails,
    loadingDetails,
    availableSeasons: playerSeasons,
    currentSeason: playerSeason,
    handlePlayerClick,
    handleSeasonChange: handlePlayerSeasonChange,
    closeDetails,
  } = usePlayerDetails();

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getChartData(position, season);
      setChartData(res.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [position, season]);

  useEffect(() => { fetchData(); }, [fetchData]);

  // Build bar data: sort by stat descending, take top N
  const barData = useMemo(() => {
    if (!chartData?.players) return [];
    return chartData.players
      .filter((p) => p.stats[stat] != null && meetsDerivedThreshold(p, stat))
      .map(p => ({
        name: p.name,
        position: p.position,
        team: p.team,
        headshot_url: p.headshot_url,
        value: p.stats[stat],
        statLabel: stat,
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, topN);
  }, [chartData, stat, topN]);

  const statOptions = useMemo(
    () => getStatOptions(position, chartData?.stat_columns || []),
    [position, chartData?.stat_columns]
  );

  useEffect(() => {
    const filteredStats = statOptions.flatMap(({ stats }) => stats);
    if (!filteredStats.length) return;
    if (!filteredStats.includes(stat)) {
      setStat(filteredStats[0]);
    }
  }, [statOptions, stat]);

  // Dynamic chart height based on number of bars
  const chartHeight = Math.max(400, barData.length * 32 + 60);

  if (loading) return <LoadingMessage message="Loading chart data..." />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="charts-container">
      <h1>Stat Charts</h1>

      <div className="charts-controls">
        <div className="control-group">
          <label>Position:</label>
          <select value={position} onChange={(e) => setPosition(e.target.value)}>
            <option value="Overall">Overall</option>
            <option value="QB">QB</option>
            <option value="RB">RB</option>
            <option value="WR">WR</option>
            <option value="TE">TE</option>
          </select>
        </div>

        {chartData?.available_seasons?.length > 1 && (
          <div className="control-group">
            <label>Season:</label>
            <select
              value={season ?? chartData.season}
              onChange={(e) => setSeason(Number(e.target.value))}
            >
              {chartData.available_seasons.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        )}

        <div className="control-group">
          <label>Stat:</label>
          <select value={stat} onChange={(e) => setStat(e.target.value)}>
            {statOptions.map(({ category, stats }) => (
              <optgroup key={category} label={category}>
                {stats.map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label>Show:</label>
          <select value={topN} onChange={(e) => setTopN(Number(e.target.value))}>
            {TOP_N_OPTIONS.map(n => (
              <option key={n} value={n}>Top {n}</option>
            ))}
          </select>
        </div>
      </div>

      {barData.length === 0 ? (
        <p className="charts-no-data">No data available for the selected stat.</p>
      ) : (
        <div className="chart-wrapper">
          <ResponsiveContainer width="100%" height={chartHeight}>
            <BarChart
              data={barData}
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
                  if (e?.value) handlePlayerClick(e.value);
                }}
              />
              <Tooltip cursor={false} content={<CustomTooltip />} />
              <Bar
                dataKey="value"
                shape={(shapeProps) => (
                  <CustomBarShape {...shapeProps} onBarClick={handlePlayerClick} />
                )}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {(playerDetails || loadingDetails) && (
        <PlayerDetailsModal
          playerDetails={playerDetails}
          loading={loadingDetails}
          onClose={closeDetails}
          availableSeasons={playerSeasons}
          currentSeason={playerSeason}
          onSeasonChange={handlePlayerSeasonChange}
        />
      )}
    </div>
  );
}
