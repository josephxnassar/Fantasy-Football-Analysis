// Weighted rankings tab with category and stat-level controls.

import { useMemo } from 'react';

import { useChartData } from '../hooks/useChartData';
import { ErrorMessage, LoadingMessage } from '../../../shared/ui';
import { RANKING_GROUPS } from './rankingGroups';
import RankingsHeader from './RankingsHeader';
import { buildRankings, getRankableGroups } from './rankingsHelpers';
import RankingsResultsTable from './RankingsResultsTable';
import RankingsWeightsPanel from './RankingsWeightsPanel';
import { useRankingsState } from './useRankingsState';
import './Rankings.css';

export default function Rankings({ onPlayerClick, onPlayerSeasonClick }) {
  const {
    position,
    setPosition,
    season,
    setSeason,
    topN,
    setTopN,
    selectedPreset,
    expandedCategories,
    categoryWeights,
    statWeights,
    setCategoryWeight,
    setStatWeight,
    resetPositionWeights,
    toggleCategoryDetails,
    handlePresetChange,
  } = useRankingsState();
  const { chartData, loading, error } = useChartData(position, season);
  const rankableGroups = useMemo(
    () => getRankableGroups(position, chartData?.stat_columns || [], RANKING_GROUPS),
    [position, chartData?.stat_columns],
  );
  const rankedPlayers = useMemo(
    () => buildRankings(chartData?.players || [], rankableGroups, categoryWeights, statWeights, topN),
    [chartData?.players, rankableGroups, categoryWeights, statWeights, topN],
  );
  const selectedSeason = season ?? chartData?.season ?? null;

  if (loading) return <LoadingMessage message="Loading ranking data..." />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="rankings-container">
      <div className="rankings-stage">
        <RankingsHeader
          position={position}
          setPosition={setPosition}
          season={season}
          setSeason={setSeason}
          topN={topN}
          setTopN={setTopN}
          availableSeasons={chartData?.available_seasons}
          currentSeason={chartData?.season}
        />

        <div className="rankings-body">
          <RankingsWeightsPanel
            rankableGroups={rankableGroups}
            selectedPreset={selectedPreset}
            handlePresetChange={handlePresetChange}
            resetPositionWeights={resetPositionWeights}
            categoryWeights={categoryWeights}
            expandedCategories={expandedCategories}
            toggleCategoryDetails={toggleCategoryDetails}
            setCategoryWeight={setCategoryWeight}
            statWeights={statWeights}
            setStatWeight={setStatWeight}
          />
          <RankingsResultsTable
            rankedPlayers={rankedPlayers}
            selectedSeason={selectedSeason}
            onPlayerClick={onPlayerClick}
            onPlayerSeasonClick={onPlayerSeasonClick}
          />
        </div>
      </div>
    </div>
  );
}
