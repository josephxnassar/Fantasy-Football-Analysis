/* Hook for managing player details modal state */

import { useState } from 'react';
import { getPlayer } from '../api';

export function usePlayerDetails() {
  const [playerDetails, setPlayerDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [playerAvailableSeasons, setPlayerAvailableSeasons] = useState([]);
  const [currentSeason, setCurrentSeason] = useState(null);
  const [currentPlayerName, setCurrentPlayerName] = useState(null);
  const [baseRating, setBaseRating] = useState(null);
  const [playerRankingData, setPlayerRankingData] = useState(null);

  const handlePlayerClick = async (playerName, rankingData = null) => {
    try {
      setLoadingDetails(true);
      setCurrentPlayerName(playerName);
      
      const response = await getPlayer(playerName);
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
      setLoadingDetails(false);
    }
  };

  const handleSeasonChange = async (season) => {
    if (!currentPlayerName) return;
    
    try {
      setLoadingDetails(true);
      setCurrentSeason(season);
      
      const response = await getPlayer(currentPlayerName, season);
      
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
      setLoadingDetails(false);
    }
  };

  const closeDetails = () => {
    setPlayerDetails(null);
    setCurrentPlayerName(null);
    setCurrentSeason(null);
    setBaseRating(null);
    setPlayerAvailableSeasons([]);
    setPlayerRankingData(null);
  };

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
