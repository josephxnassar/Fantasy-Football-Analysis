// Hook for managing player-details modal state.

import { useCallback, useEffect, useRef, useState } from 'react';
import { getPlayer } from '../../../api';

export function usePlayerDetails() {
  const [playerDetails, setPlayerDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [detailsError, setDetailsError] = useState(null);

  const [playerAvailableSeasons, setPlayerAvailableSeasons] = useState([]);
  const [currentSeason, setCurrentSeason] = useState(null);
  const [currentPlayerName, setCurrentPlayerName] = useState(null);

  const playerRequestIdRef = useRef(0);
  const seasonRequestIdRef = useRef(0);

  useEffect(() => {
    return () => {
      playerRequestIdRef.current += 1;
      seasonRequestIdRef.current += 1;
    };
  }, []);

  const loadPlayerForModal = useCallback(async (playerName, season = null, errorMessage = 'Failed to load player details.') => {
    const requestId = ++playerRequestIdRef.current;
    seasonRequestIdRef.current += 1;

    try {
      setLoadingDetails(true);
      setDetailsError(null);
      setCurrentPlayerName(playerName);

      const response = await getPlayer(playerName, season);
      if (requestId !== playerRequestIdRef.current) 
        return;

      setPlayerDetails(response.data);

      const seasons = response.data.available_seasons || [];
      setPlayerAvailableSeasons(seasons);

      const mostRecentSeason = seasons.length > 0 ? seasons[0] : null;
      setCurrentSeason(season ?? mostRecentSeason);
    } catch (err) {
      if (requestId === playerRequestIdRef.current) {
        setDetailsError(errorMessage);
        setPlayerDetails(null);
        setCurrentPlayerName(null);
        setCurrentSeason(null);
        setPlayerAvailableSeasons([]);
      }
      console.error(`Failed to load player details: ${err.message}`);
    } finally {
      if (requestId === playerRequestIdRef.current) {
        setLoadingDetails(false);
      }
    }
  }, []);

  const handlePlayerClick = useCallback(async (playerName) => {
    await loadPlayerForModal(playerName);
  }, [loadPlayerForModal]);

  const handlePlayerSeasonClick = useCallback(async (playerName, season) => {
    const normalizedSeason = Number(season);
    if (!Number.isFinite(normalizedSeason)) {
      await loadPlayerForModal(playerName);
      return;
    }

    await loadPlayerForModal(playerName, normalizedSeason, `Failed to load ${normalizedSeason} season data.`);
  }, [loadPlayerForModal]);

  const handleSeasonChange = useCallback(async (season) => {
    if (!currentPlayerName) 
      return;

    const requestId = ++seasonRequestIdRef.current;

    try {
      setLoadingDetails(true);
      setDetailsError(null);

      const response = await getPlayer(currentPlayerName, season);
      if (requestId !== seasonRequestIdRef.current) return;
      setPlayerDetails(response.data);
      setCurrentSeason(season);
      setPlayerAvailableSeasons(response.data.available_seasons || []);
    } catch (err) {
      if (requestId === seasonRequestIdRef.current)
        setDetailsError(`Failed to load ${season} season data.`);
      console.error(`Failed to load season data: ${err.message}`);
    } finally {
      if (requestId === seasonRequestIdRef.current)
        setLoadingDetails(false);
    }
  }, [currentPlayerName]);

  const closeDetails = useCallback(() => {
    playerRequestIdRef.current += 1;
    seasonRequestIdRef.current += 1;
    setLoadingDetails(false);
    setDetailsError(null);
    setPlayerDetails(null);
    setCurrentPlayerName(null);
    setCurrentSeason(null);
    setPlayerAvailableSeasons([]);
  }, []);

  return {
    playerDetails,
    loadingDetails,
    detailsError,
    availableSeasons: playerAvailableSeasons,
    currentSeason,
    handlePlayerClick,
    handlePlayerSeasonClick,
    handleSeasonChange,
    closeDetails,
  };
}
