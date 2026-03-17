/**
 * File overview: Component for Charts within the statistics charts feature.
 */

import { Suspense, lazy, useEffect, useMemo } from 'react';

import { getStatLabel } from '../../../shared/utils/statDefinitions';
import { ErrorMessage, LoadingMessage, StatTooltip } from '../../../shared/ui';
import ChartControls from './ChartControls';
import { VIEW_META, VIEWS_USING_STAT } from './ChartsMeta';
import { useAverageVsUpsideData } from './consistency-upside/useAverageVsUpsideData';
import { useLeaderboardData } from './leaderboard/useLeaderboardData';
import { useSeasonTrendsData } from './season-trends/useSeasonTrendsData';
import { getNextChartStat, getNextTrendPlayer, useChartsState } from './useChartsState';
import './Charts.css';

const LeaderboardChart = lazy(() => import('./leaderboard/LeaderboardChart'));
const AverageVsUpsideChart = lazy(() => import('./consistency-upside/AverageVsUpsideChart'));
const SeasonTrendsChart = lazy(() => import('./season-trends/SeasonTrendsChart'));
const VIEW_LOADING_MESSAGES = {
  leaderboard: 'Loading leaderboard chart...',
  'consistency-upside': 'Loading Average vs Upside chart...',
  trend: 'Loading season trends chart...',
};

export default function Charts({ onPlayerClick, onPlayerSeasonClick }) {
  const { view, setView, position, setPosition, season, setSeason, stat, setStat, trendPlayer, setTrendPlayer } =
    useChartsState();
  const leaderboardData = useLeaderboardData({
    position,
    season,
    stat,
    enabled: view === 'leaderboard',
  });
  const consistencyData = useAverageVsUpsideData({
    position,
    season,
    enabled: view === 'consistency-upside',
  });
  const trendData = useSeasonTrendsData({
    stat,
    trendPlayer,
    enabled: view === 'trend',
  });
  const activeData = view === 'trend' ? trendData : view === 'consistency-upside' ? consistencyData : leaderboardData;
  const chartData = activeData.chartData;
  const loading = activeData.loading;
  const error = activeData.error;
  const chartSeason = activeData.chartSeason;
  const statOptions = view === 'trend' ? trendData.statOptions : view === 'leaderboard' ? leaderboardData.statOptions : [];
  const defaultStat = view === 'trend' ? trendData.defaultStat : view === 'leaderboard' ? leaderboardData.defaultStat : null;
  const availableStatOptions = useMemo(
    () => (view === 'trend' ? trendData.availableStatOptions : view === 'leaderboard' ? leaderboardData.availableStatOptions : []),
    [leaderboardData.availableStatOptions, trendData.availableStatOptions, view],
  );
  const trendPlayerOptions = useMemo(() => (view === 'trend' ? trendData.trendPlayerOptions : []), [trendData.trendPlayerOptions, view]);

  useEffect(() => {
    const nextStat = getNextChartStat(stat, defaultStat, availableStatOptions);
    if (nextStat !== stat) {
      setStat(nextStat);
    }
  }, [availableStatOptions, defaultStat, setStat, stat]);

  useEffect(() => {
    const nextTrendPlayer = getNextTrendPlayer(view, trendPlayer, trendPlayerOptions, view === 'trend' ? trendData.loading : false);
    if (nextTrendPlayer !== trendPlayer) {
      setTrendPlayer(nextTrendPlayer);
    }
  }, [setTrendPlayer, trendData.loading, trendPlayer, trendPlayerOptions, view]);

  const activeViewMeta = VIEW_META[view] || VIEW_META.leaderboard;
  const trendEnabled = view === 'trend';
  const consistencyEnabled = view === 'consistency-upside';

  if (loading) return <LoadingMessage message="Loading chart data..." />;
  if (error) return <ErrorMessage message={error} />;
  if (consistencyEnabled && consistencyData.consistencyLoading) return <LoadingMessage message="Loading Average vs Upside chart..." />;
  if (consistencyEnabled && consistencyData.consistencyError) return <ErrorMessage message={consistencyData.consistencyError} />;
  if (trendEnabled && trendData.trendLoading) return <LoadingMessage message="Loading season trends..." />;
  if (trendEnabled && trendData.trendError) return <ErrorMessage message={trendData.trendError} />;

  return (
    <div className="charts-container">
      <div className="charts-stage">
        <div className={`charts-panel charts-panel--header ${view === 'leaderboard' ? 'charts-panel--leaderboard' : ''}`}>
          <div className="charts-copy">
            <div className="charts-kicker-with-help">
              <p className="charts-kicker">{activeViewMeta.kicker}</p>
              <StatTooltip label={activeViewMeta.kicker} description={activeViewMeta.description} iconSize={14} />
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
          />
        </div>

        <Suspense fallback={<LoadingMessage message={VIEW_LOADING_MESSAGES[view] || 'Loading chart view...'} />}>
          {view === 'leaderboard' && (
            <LeaderboardChart
              data={leaderboardData.barData}
              stat={stat}
              season={chartSeason}
              onPlayerClick={onPlayerClick}
              onPlayerSeasonClick={onPlayerSeasonClick}
            />
          )}
          {view === 'consistency-upside' && (
            <AverageVsUpsideChart
              data={consistencyData.consistencyData?.players || []}
              season={chartSeason}
              onPlayerClick={onPlayerClick}
              onPlayerSeasonClick={onPlayerSeasonClick}
            />
          )}
          {view === 'trend' && (
            <SeasonTrendsChart
              data={trendData.trendSeries}
              playerName={trendPlayer}
              stat={stat}
              statLabel={getStatLabel(stat)}
              onPlayerClick={onPlayerClick}
              onPlayerSeasonClick={onPlayerSeasonClick}
            />
          )}
        </Suspense>
      </div>
    </div>
  );
}
