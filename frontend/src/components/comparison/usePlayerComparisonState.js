// Hook for comparison filters, player options, and winner calculations.

import { useMemo, useState } from 'react';

import { useChartData } from '../../hooks/useChartData';
import { buildComparisonRows, buildComparisonWins, getWinningSlotIdsForStat, getWinningSlotIdsForWeeks } from './comparisonHelpers';
import { useComparisonSlots } from './useComparisonSlots';

export { MAX_COMPARE_PLAYERS } from './useComparisonSlots';

export function usePlayerComparisonState() {
  const [positionProfile, setPositionProfile] = useState('Overall');
  const {
    comparisonSlots,
    selectionError,
    handlePlayerSelect,
    handleSeasonChange,
    handleRemovePlayer,
    resetForPositionProfile,
  } = useComparisonSlots();
  const { chartData, loading: playerOptionsLoading, error: playerOptionsError } = useChartData(positionProfile, null);

  const comparisonRows = buildComparisonRows(positionProfile);
  const playerOptions = useMemo(() => {
    const players = chartData?.players || [];
    return players
      .map((player) => player.name)
      .filter(Boolean)
      .sort((a, b) => a.localeCompare(b));
  }, [chartData?.players]);
  const selectedPlayers = comparisonSlots.filter((slot) => Boolean(slot.playerName));
  const statWinnersByKey = useMemo(
    () =>
      Object.fromEntries(
        comparisonRows
          .filter((row) => row.type === 'stat')
          .map((row) => [row.statKey, getWinningSlotIdsForStat(row.statKey, selectedPlayers)])
      ),
    [comparisonRows, selectedPlayers]
  );
  const weeksWinners = useMemo(() => getWinningSlotIdsForWeeks(selectedPlayers), [selectedPlayers]);
  const winCountsBySlot = useMemo(
    () => buildComparisonWins(comparisonRows, selectedPlayers),
    [comparisonRows, selectedPlayers]
  );

  const handlePositionProfileChange = (nextPosition) => {
    setPositionProfile(nextPosition);
    resetForPositionProfile(nextPosition);
  };

  return {
    positionProfile,
    comparisonSlots,
    selectionError,
    playerOptionsLoading,
    playerOptionsError,
    playerOptions,
    selectedPlayers,
    comparisonRows,
    statWinnersByKey,
    weeksWinners,
    winCountsBySlot,
    handlePositionProfileChange,
    handlePlayerSelect,
    handleSeasonChange,
    handleRemovePlayer,
  };
}
