/* Hook for managing player details modal state */

import { useCallback, useEffect, useRef, useState } from 'react';
import { getPlayer } from '../api';

export function usePlayerDetails() {
  const [playerDetails, setPlayerDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [playerAvailableSeasons, setPlayerAvailableSeasons] = useState([]);
  const [currentSeason, setCurrentSeason] = useState(null);
  const [currentPlayerName, setCurrentPlayerName] = useState(null);
  const [baseRating, setBaseRating] = useState(null);
  const [playerRankingData, setPlayerRankingData] = useState(null);
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

  const handlePlayerClick = useCallback(async (playerName, rankingData = null) => {
    const requestId = ++playerRequestIdRef.current;
    seasonRequestIdRef.current += 1;

    try {
      setLoadingDetails(true);
      setCurrentPlayerName(playerName);
      
      const response = await getPlayer(playerName);
      if (!mountedRef.current || requestId !== playerRequestIdRef.current) return;

      const resolvedRankingData = rankingData || response.data?.ranking_data || null;
      setPlayerRankingData(resolvedRankingData);
      setPlayerDetails(response.data);
      
      setBaseRating(
        resolvedRankingData?.redraft_rating ||
        response.data.stats?.redraft_rating ||
        null
      );
      
      const seasons = response.data.available_seasons || [];
      setPlayerAvailableSeasons(seasons);
      
      // Default to most recent season (first in list, which is sorted descending)
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
    const requestId = ++seasonRequestIdRef.current;
    
    try {
      setLoadingDetails(true);
      setCurrentSeason(season);
      
      const response = await getPlayer(currentPlayerName, season);
      if (!mountedRef.current || requestId !== seasonRequestIdRef.current) return;
      
      // Keep the base rating from the initial load
      const nextDetails = baseRating !== null
        ? {
            ...response.data,
            stats: {
              ...response.data.stats,
              redraft_rating: baseRating,
            },
          }
        : response.data;

      setPlayerDetails(nextDetails);
    } catch (err) {
      console.error(`Failed to load season data: ${err.message}`);
    } finally {
      if (mountedRef.current && requestId === seasonRequestIdRef.current) {
        setLoadingDetails(false);
      }
    }
  }, [baseRating, currentPlayerName]);

  const closeDetails = useCallback(() => {
    playerRequestIdRef.current += 1;
    seasonRequestIdRef.current += 1;
    setLoadingDetails(false);
    setPlayerDetails(null);
    setCurrentPlayerName(null);
    setCurrentSeason(null);
    setBaseRating(null);
    setPlayerAvailableSeasons([]);
    setPlayerRankingData(null);
  }, []);

  return {
    playerDetails,
    loadingDetails,
    availableSeasons: playerAvailableSeasons,
    currentSeason,
    playerRankingData,
    handlePlayerClick,
    handleSeasonChange,
    closeDetails
  };
}
