/* Hook for player-comparison state, data loading, and winner calculations. */

import { useMemo, useRef, useState } from 'react';

import { getPlayer } from '../../api';
import { useChartData } from '../../hooks/useChartData';
import { buildComparisonRows, buildComparisonWins, getWinningSlotIdsForStat, getWinningSlotIdsForWeeks } from './comparisonHelpers';

export const MAX_COMPARE_PLAYERS = 3;

const EMPTY_SLOT = {
  playerName: '',
  team: null,
  position: null,
  season: null,
  weeksPlayed: null,
  availableSeasons: [],
  stats: null,
  loading: false,
  error: null,
};

function createInitialSlots() {
  return Array.from({ length: MAX_COMPARE_PLAYERS }, (_, index) => ({
    id: index + 1,
    ...EMPTY_SLOT,
  }));
}

function getWeeksPlayedForSeason(weeklyStats, season) {
  if (!Array.isArray(weeklyStats) || season === null || season === undefined) return null;
  return weeklyStats.filter((week) => Number(week?.season) === Number(season)).length;
}

export function usePlayerComparisonState() {
  const [positionProfile, setPositionProfile] = useState('Overall');
  const [comparisonSlots, setComparisonSlots] = useState(createInitialSlots);
  const [selectionError, setSelectionError] = useState(null);
  const requestIdsBySlotRef = useRef({});
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

  const updateSlot = (slotId, updater) => {
    setComparisonSlots((previous) =>
      previous.map((slot) => (slot.id === slotId ? updater(slot) : slot))
    );
  };

  const clearSlot = (slotId) => {
    delete requestIdsBySlotRef.current[slotId];
    updateSlot(slotId, () => ({ id: slotId, ...EMPTY_SLOT }));
  };

  const loadPlayerDetails = async (slotId, playerName, season = null) => {
    const requestId = (requestIdsBySlotRef.current[slotId] || 0) + 1;
    requestIdsBySlotRef.current[slotId] = requestId;

    updateSlot(slotId, (slot) => ({ ...slot, playerName, loading: true, error: null }));

    try {
      const response = await getPlayer(playerName, season);
      if (requestIdsBySlotRef.current[slotId] !== requestId) return;

      const payload = response.data;
      const availableSeasons = payload.available_seasons || [];
      const resolvedSeason = season ?? (availableSeasons[0] ?? null);
      const weeksPlayed = getWeeksPlayedForSeason(payload.weekly_stats || [], resolvedSeason);

      updateSlot(slotId, (slot) => ({
        ...slot,
        playerName: payload.name,
        team: payload.team,
        position: payload.position,
        season: resolvedSeason,
        weeksPlayed,
        availableSeasons,
        stats: payload.stats || {},
        loading: false,
        error: null,
      }));
    } catch (err) {
      if (requestIdsBySlotRef.current[slotId] !== requestId) return;
      const message = err?.message || 'Failed to load player details.';
      updateSlot(slotId, (slot) => ({
        ...slot,
        loading: false,
        error: message,
      }));
    }
  };

  const handlePositionProfileChange = (nextPosition) => {
    setPositionProfile(nextPosition);
    setSelectionError(null);
    requestIdsBySlotRef.current = {};
    setComparisonSlots(createInitialSlots());
  };

  const handlePlayerSelect = (slotId, playerName) => {
    setSelectionError(null);
    if (!playerName) {
      clearSlot(slotId);
      return;
    }

    const duplicate = comparisonSlots.some((slot) => slot.id !== slotId && slot.playerName === playerName);
    if (duplicate) {
      setSelectionError('Each slot must use a different player.');
      return;
    }

    void loadPlayerDetails(slotId, playerName, null);
  };

  const handleSeasonChange = (slotId, nextSeasonValue) => {
    const slot = comparisonSlots.find((candidate) => candidate.id === slotId);
    const nextSeason = Number(nextSeasonValue);
    if (!slot || !slot.playerName || Number.isNaN(nextSeason)) return;
    void loadPlayerDetails(slotId, slot.playerName, nextSeason);
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
  };
}
