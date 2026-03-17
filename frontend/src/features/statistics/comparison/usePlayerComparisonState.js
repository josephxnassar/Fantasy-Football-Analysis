import { useMemo } from 'react';

import { useStatisticsData } from '../useStatisticsData';
import { buildComparisonRows, buildComparisonWins, getWinningSlotIdsForStat, getWinningSlotIdsForWeeks } from './comparisonHelpers';
import { useComparisonSlots } from './useComparisonSlots';

export { MAX_COMPARE_PLAYERS } from './useComparisonSlots';

function getComparisonProfileLabel(profile, selectedPlayers) {
  if (selectedPlayers.length === 0) return 'Select players';
  if (selectedPlayers.some((slot) => slot.loading || (!slot.position && !slot.error))) return 'Detecting...';
  return profile === 'CrossPosition' ? 'Cross-Position' : profile;
}

function isComparisonPosition(position) {
  return position === 'QB' || position === 'RB' || position === 'WR' || position === 'TE';
}

function getComparisonProfile(selectedPlayers) {
  const positions = [...new Set(selectedPlayers.map((slot) => slot.position).filter(isComparisonPosition))];
  return positions.length === 1 ? positions[0] : 'CrossPosition';
}

export function usePlayerComparisonState() {
  const { comparisonSlots, selectionError, handlePlayerSelect, handleSeasonChange, handleRemovePlayer } = useComparisonSlots();
  const { statisticsData, loading: playerOptionsLoading, error: playerOptionsError } = useStatisticsData('Overall', null);

  const playerOptions = useMemo(() => {
    const players = statisticsData?.players || [];
    return players
      .map((player) => player.name)
      .filter(Boolean)
      .sort((a, b) => a.localeCompare(b));
  }, [statisticsData?.players]);

  const selectedPlayers = comparisonSlots.filter((slot) => Boolean(slot.playerName));
  const comparisonProfile = useMemo(
    () => getComparisonProfile(selectedPlayers),
    [selectedPlayers],
  );
  const comparisonProfileLabel = getComparisonProfileLabel(comparisonProfile, selectedPlayers);
  const comparisonRows = useMemo(() => buildComparisonRows(comparisonProfile), [comparisonProfile]);
  const statWinnersByKey = useMemo(
    () =>
      Object.fromEntries(
        comparisonRows
          .filter((row) => row.type === 'stat')
          .map((row) => [row.statKey, getWinningSlotIdsForStat(row.statKey, selectedPlayers)]),
      ),
    [comparisonRows, selectedPlayers],
  );
  const weeksWinners = useMemo(() => getWinningSlotIdsForWeeks(selectedPlayers), [selectedPlayers]);
  const winCountsBySlot = useMemo(() => buildComparisonWins(comparisonRows, selectedPlayers), [comparisonRows, selectedPlayers]);

  return {
    comparisonSlots,
    selectionError,
    playerOptionsLoading,
    playerOptionsError,
    playerOptions,
    selectedPlayers,
    comparisonProfileLabel,
    comparisonRows,
    statWinnersByKey,
    weeksWinners,
    winCountsBySlot,
    handlePlayerSelect,
    handleSeasonChange,
    handleRemovePlayer,
  };
}
