/**
 * File overview: Component for Rankings within the rankings feature.
 */

import { useMemo } from 'react';

import { OVERALL_RANKING_GROUPS } from '../../../shared/utils/statMeta';
import { ErrorMessage, LoadingMessage } from '../../../shared/ui';
import { useStatisticsData } from '../useStatisticsData';
import RankingsHeader from './RankingsHeader';
import { buildRankings, getRankableGroups } from './rankingsHelpers';
import RankingsResultsTable from './RankingsResultsTable';
import RankingsWeightsPanel from './RankingsWeightsPanel';
import { useRankingsState } from './useRankingsState';
import './Rankings.css';

export default function Rankings({ onPlayerClick, onPlayerSeasonClick }) {
  const {
    season,
    setSeason,
    selectedPreset,
    expandedCategories,
    categoryWeights,
    statWeights,
    setCategoryWeight,
    setStatWeight,
    resetWeights,
    toggleCategoryDetails,
    handlePresetChange,
  } = useRankingsState();
  const { statisticsData, loading, error } = useStatisticsData('Overall', season);
  const rankableGroups = useMemo(
    () => getRankableGroups(OVERALL_RANKING_GROUPS, statisticsData?.stat_columns || []),
    [statisticsData?.stat_columns],
  );
  const rankedPlayers = useMemo(
    () => buildRankings(statisticsData?.players || [], rankableGroups, categoryWeights, statWeights),
    [statisticsData?.players, rankableGroups, categoryWeights, statWeights],
  );
  const selectedSeason = season ?? statisticsData?.season ?? null;

  if (loading) return <LoadingMessage message="Loading ranking data..." />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="rankings-container">
      <div className="rankings-stage">
        <RankingsHeader
          season={season}
          setSeason={setSeason}
          availableSeasons={statisticsData?.available_seasons}
          currentSeason={statisticsData?.season}
        />

        <div className="rankings-body">
          <RankingsWeightsPanel
            rankableGroups={rankableGroups}
            selectedPreset={selectedPreset}
            handlePresetChange={handlePresetChange}
            resetWeights={resetWeights}
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
