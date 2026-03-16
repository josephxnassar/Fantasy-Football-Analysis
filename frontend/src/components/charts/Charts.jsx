// Multi-view charts tab for leaderboards, trends, and profile scatter plots.

import { Suspense, lazy } from 'react';

import { getStatLabel } from '../../utils/statDefinitions';
import { ErrorMessage, LoadingMessage, StatTooltip } from '../common';
import ChartControls from './ChartControls';
import { VIEW_META, VIEWS_USING_STAT } from './chartsConfig';
import { useChartsData } from './useChartsData';
import { useChartsState, useChartsStateValidation } from './useChartsState';
import './Charts.css';

const LeaderboardChart = lazy(() => import('./LeaderboardChart'));
const AverageVsUpsideChart = lazy(() => import('./AverageVsUpsideChart'));
const SeasonTrendsChart = lazy(() => import('./SeasonTrendsChart'));
const VIEW_LOADING_MESSAGES = {
  leaderboard: 'Loading leaderboard chart...',
  'consistency-upside': 'Loading Average vs Upside chart...',
  trend: 'Loading season trends chart...',
};

export default function Charts({ onPlayerClick, onPlayerSeasonClick }) {
  const {
    view,
    setView,
    position,
    setPosition,
    season,
    setSeason,
    stat,
    setStat,
    topN,
    setTopN,
    trendPlayer,
    setTrendPlayer,
  } = useChartsState();
  const {
    chartData,
    loading,
    error,
    consistencyEnabled,
    consistencyData,
    consistencyLoading,
    consistencyError,
    trendEnabled,
    trendLoading,
    trendError,
    barData,
    statOptions,
    availableStatOptions,
    rankedTrendPlayers,
    trendPlayerOptions,
    trendSeries,
    chartSeason,
  } = useChartsData({ view, position, season, stat, topN, trendPlayer });
  useChartsStateValidation({ view, stat, setStat, availableStatOptions, trendPlayer, setTrendPlayer, rankedTrendPlayers, trendPlayerOptions });

  const activeViewMeta = VIEW_META[view] || VIEW_META.leaderboard;

  if (loading)
    return <LoadingMessage message="Loading chart data..." />;
  if (error)
    return <ErrorMessage message={error} />;
  if (consistencyEnabled && consistencyLoading)
    return <LoadingMessage message="Loading Average vs Upside chart..." />;
  if (consistencyEnabled && consistencyError)
    return <ErrorMessage message={consistencyError} />;
  if (trendEnabled && trendLoading)
    return <LoadingMessage message="Loading season trends..." />;
  if (trendEnabled && trendError)
    return <ErrorMessage message={trendError} />;

  return (
    <div className="charts-container">
      <div className="charts-stage">
        <div className={`charts-panel charts-panel--header ${view === 'leaderboard' ? 'charts-panel--leaderboard' : ''}`}>
          <div className="charts-copy">
            <div className="charts-kicker-with-help">
              <p className="charts-kicker">{activeViewMeta.kicker}</p>
              <StatTooltip label={activeViewMeta.kicker} description={activeViewMeta.description} iconSize={14}/>
            </div>
            <h1>Stat Charts</h1>
          </div>

          <ChartControls view={view} setView={setView} position={position} setPosition={setPosition} chartData={chartData} season={season} setSeason={setSeason} stat={stat} setStat={setStat} statOptions={statOptions} showStatControl={VIEWS_USING_STAT.has(view)} showPositionControl showSeasonControl={view !== 'trend'} trendPlayer={trendPlayer} setTrendPlayer={setTrendPlayer} trendPlayerOptions={trendPlayerOptions} showTrendPlayerControl={view === 'trend'} topN={topN} setTopN={setTopN} showTopNControl={view !== 'trend'}/>
        </div>

        <Suspense fallback={<LoadingMessage message={VIEW_LOADING_MESSAGES[view] || 'Loading chart view...'} />}>
          {view === 'leaderboard' && (<LeaderboardChart data={barData} stat={stat} season={chartSeason} onPlayerClick={onPlayerClick} onPlayerSeasonClick={onPlayerSeasonClick}/>)}
          {view === 'consistency-upside' && (<AverageVsUpsideChart data={consistencyData?.players || []} season={chartSeason} onPlayerClick={onPlayerClick} onPlayerSeasonClick={onPlayerSeasonClick}/>)}
          {view === 'trend' && (<SeasonTrendsChart data={trendSeries} playerName={trendPlayer} stat={stat} statLabel={getStatLabel(stat)} onPlayerClick={onPlayerClick} onPlayerSeasonClick={onPlayerSeasonClick}/>)}
        </Suspense>
      </div>
    </div>
  );
}
