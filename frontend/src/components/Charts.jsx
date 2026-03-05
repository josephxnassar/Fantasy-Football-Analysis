/* Multi-view charts tab for leaderboards, trends, and profile scatter plots. */

import { useEffect, useMemo, useState } from 'react';

import { useChartData } from '../hooks/useChartData';
import { useConsistencyData } from '../hooks/useConsistencyData';
import { useSessionStorageObject } from '../hooks/useSessionStorageObject';
import { useSeasonChartData } from '../hooks/useSeasonChartData';
import { getStatLabel } from '../utils/statDefinitions';
import { PRODUCTION_GROUPS } from '../utils/statMeta';
import { ErrorMessage, LoadingMessage, StatTooltip } from './common';
import ChartControls from './charts/ChartControls';
import AverageVsUpsideChart from './charts/AverageVsUpsideChart';
import LeaderboardChart from './charts/LeaderboardChart';
import SeasonTrendsChart from './charts/SeasonTrendsChart';
import {
  DEFAULT_STAT,
  VIEW_META,
  VIEWS_USING_STAT,
} from './charts/chartsConfig';
import {
  buildBarData,
  getStatOptions,
} from './charts/chartsHelpers';
import './Charts.css';

const CHART_UI_STORAGE_KEY = 'chartsUi';

export default function Charts({ onPlayerClick }) {
  const [chartUiState, setChartUiState] = useSessionStorageObject(CHART_UI_STORAGE_KEY, {});
  const initialPosition = chartUiState.position || 'Overall';

  // UI controls for the chart query.
  const [view, setView] = useState(chartUiState.view || 'leaderboard');
  const [position, setPosition] = useState(initialPosition);
  const [season, setSeason] = useState(null);
  const [stat, setStat] = useState(chartUiState.stat || DEFAULT_STAT[initialPosition] || DEFAULT_STAT.Overall);
  const [topN, setTopN] = useState(chartUiState.topN || 20);
  const [trendPlayer, setTrendPlayer] = useState(chartUiState.trendPlayer || '');
  const effectivePosition = view === 'trend' ? 'Overall' : position;
  const effectiveSeason = view === 'trend' ? null : season;

  // Server payload for selected position + season.
  const { chartData, loading, error } = useChartData(effectivePosition, effectiveSeason);
  const consistencyEnabled = view === 'consistency-upside';
  const trendEnabled = view === 'trend';
  const { data: consistencyData, loading: consistencyLoading, error: consistencyError } = useConsistencyData(effectivePosition, effectiveSeason, topN, consistencyEnabled);
  const { data: trendData, loading: trendLoading, error: trendError } = useSeasonChartData(effectivePosition, trendPlayer, stat, trendEnabled);

  // Flatten API rows into sorted chart bars for the selected stat.
  const barData = useMemo(() => buildBarData(chartData?.players, stat, topN), [chartData?.players, stat, topN]);

  // Build grouped stat picker options from available columns + position config.
  const statOptions = useMemo(
    () => getStatOptions(effectivePosition, chartData?.stat_columns || [], PRODUCTION_GROUPS),
    [effectivePosition, chartData?.stat_columns]
  );
  const availableStatOptions = useMemo(() => statOptions.flatMap(({ stats }) => stats), [statOptions]);
  const rankedTrendPlayers = useMemo(
    () => buildBarData(chartData?.players, stat, chartData?.players?.length || 0).map((row) => row.name),
    [chartData?.players, stat]
  );
  const trendPlayerOptions = useMemo(
    () => rankedTrendPlayers.slice().sort((a, b) => a.localeCompare(b)),
    [rankedTrendPlayers]
  );
  const trendSeries = trendData?.points || [];

  useEffect(() => {
    // Keep selected stat valid when position/season payload changes.
    if (!availableStatOptions.length) return;
    if (!availableStatOptions.includes(stat)) {
      setStat(availableStatOptions[0]);
    }
  }, [availableStatOptions, stat]);

  useEffect(() => {
    if (view !== 'trend') return;
    if (!trendPlayerOptions.length) {
      if (trendPlayer) setTrendPlayer('');
      return;
    }
    if (!trendPlayer || !trendPlayerOptions.includes(trendPlayer)) {
      setTrendPlayer(rankedTrendPlayers[0] || trendPlayerOptions[0]);
    }
  }, [view, trendPlayerOptions, rankedTrendPlayers, trendPlayer]);

  useEffect(() => {
    setChartUiState({ view, position, topN, stat, trendPlayer });
  }, [view, position, topN, stat, trendPlayer, setChartUiState]);

  const activeViewMeta = VIEW_META[view] || VIEW_META.leaderboard;

  if (loading) return <LoadingMessage message="Loading chart data..." />;
  if (error) return <ErrorMessage message={error} />;
  if (consistencyEnabled && consistencyLoading) return <LoadingMessage message="Loading Average vs Upside chart..." />;
  if (consistencyEnabled && consistencyError) return <ErrorMessage message={consistencyError} />;
  if (trendEnabled && trendLoading) return <LoadingMessage message="Loading season trends..." />;
  if (trendEnabled && trendError) return <ErrorMessage message={trendError} />;

  return (
    <div className="charts-container">
      <div className="charts-stage">
        <div className={`charts-panel charts-panel--header ${view === 'leaderboard' ? 'charts-panel--leaderboard' : ''}`}>
          <div className="charts-copy">
            <div className="charts-kicker-with-help">
              <p className="charts-kicker">{activeViewMeta.kicker}</p>
              <StatTooltip
                label={activeViewMeta.kicker}
                description={activeViewMeta.description}
                iconSize={14}
              />
            </div>
            <h1>Stat Charts</h1>
          </div>

          <ChartControls
            view={view}
            setView={setView}
            position={position}
            setPosition={setPosition}
            chartData={chartData}
            season={season}
            setSeason={setSeason}
            stat={stat}
            setStat={setStat}
            statOptions={statOptions}
            showStatControl={VIEWS_USING_STAT.has(view)}
            showPositionControl={view !== 'trend'}
            showSeasonControl={view !== 'trend'}
            trendPlayer={trendPlayer}
            setTrendPlayer={setTrendPlayer}
            trendPlayerOptions={trendPlayerOptions}
            showTrendPlayerControl={view === 'trend'}
            topN={topN}
            setTopN={setTopN}
            showTopNControl={view !== 'trend'}
          />
        </div>

        {view === 'leaderboard' && (
          <LeaderboardChart data={barData} onPlayerClick={onPlayerClick} />
        )}

        {view === 'consistency-upside' && (
          <AverageVsUpsideChart data={consistencyData?.players || []} onPlayerClick={onPlayerClick} />
        )}

        {view === 'trend' && (
          <SeasonTrendsChart
            data={trendSeries}
            playerName={trendPlayer}
            statLabel={getStatLabel(stat)}
            onPlayerClick={onPlayerClick}
          />
        )}
      </div>
    </div>
  );
}
