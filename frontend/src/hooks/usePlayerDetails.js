/* Hook for managing player details modal state */

import { useCallback, useEffect, useRef, useState } from 'react';
import { getPlayer } from '../api';

export function usePlayerDetails() {
  // Full player payload used by PlayerDetailsModal.
  const [playerDetails, setPlayerDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  // Season selector state for the active player.
  const [playerAvailableSeasons, setPlayerAvailableSeasons] = useState([]);
  const [currentSeason, setCurrentSeason] = useState(null);
  const [currentPlayerName, setCurrentPlayerName] = useState(null);

  // Request tokens prevent stale async responses from overwriting fresh state.
  const playerRequestIdRef = useRef(0);
  const seasonRequestIdRef = useRef(0);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      playerRequestIdRef.current += 1;
      seasonRequestIdRef.current += 1;
    };
  }, []);

  const handlePlayerClick = useCallback(async (playerName) => {
    // New player request invalidates pending season-specific requests.
    const requestId = ++playerRequestIdRef.current;
    seasonRequestIdRef.current += 1;

    try {
      setLoadingDetails(true);
      setCurrentPlayerName(playerName);
      
      const response = await getPlayer(playerName);
      if (!mountedRef.current || requestId !== playerRequestIdRef.current) return;

      setPlayerDetails(response.data);

      const seasons = response.data.available_seasons || [];
      setPlayerAvailableSeasons(seasons);
      
      // API season list is sorted descending; first entry is most recent.
      const mostRecentSeason = seasons.length > 0 ? seasons[0] : null;
      setCurrentSeason(mostRecentSeason);
    } catch (err) {
      console.error(`Failed to load player details: ${err.message}`);
    } finally {
      if (mountedRef.current && requestId === playerRequestIdRef.current) {
        setLoadingDetails(false);
      }
    }
  }, []);

  const handleSeasonChange = useCallback(async (season) => {
    if (!currentPlayerName) return;

    // Track season request separately so rapid season clicks stay safe.
    const requestId = ++seasonRequestIdRef.current;
    
    try {
      setLoadingDetails(true);
      setCurrentSeason(season);
      
      const response = await getPlayer(currentPlayerName, season);
      if (!mountedRef.current || requestId !== seasonRequestIdRef.current) return;
      setPlayerDetails(response.data);
    } catch (err) {
      console.error(`Failed to load season data: ${err.message}`);
    } finally {
      if (mountedRef.current && requestId === seasonRequestIdRef.current) {
        setLoadingDetails(false);
      }
    }
  }, [currentPlayerName]);

  const closeDetails = useCallback(() => {
    // Bump request tokens to ignore any late async responses.
    playerRequestIdRef.current += 1;
    seasonRequestIdRef.current += 1;
    setLoadingDetails(false);
    setPlayerDetails(null);
    setCurrentPlayerName(null);
    setCurrentSeason(null);
    setPlayerAvailableSeasons([]);
  }, []);

  return {
    playerDetails,
    loadingDetails,
    availableSeasons: playerAvailableSeasons,
    currentSeason,
    handlePlayerClick,
    handleSeasonChange,
    closeDetails
  };
}
