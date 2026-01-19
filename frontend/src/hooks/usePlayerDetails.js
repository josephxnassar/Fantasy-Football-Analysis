import { useState } from 'react';
import { getPlayer } from '../api';

export function usePlayerDetails() {
  const [playerDetails, setPlayerDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [playerAvailableSeasons, setPlayerAvailableSeasons] = useState([]);
  const [currentSeason, setCurrentSeason] = useState(null);
  const [currentPlayerName, setCurrentPlayerName] = useState(null);
  const [baseRating, setBaseRating] = useState(null);
  const [playerGrade, setPlayerGrade] = useState(null);

  const handlePlayerClick = async (playerName, grade = null) => {
    try {
      setLoadingDetails(true);
      setCurrentPlayerName(playerName);
      setCurrentSeason(null); // Reset to average view
      setPlayerGrade(grade);
      
      // Fetch averaged data (with rating)
      const response = await getPlayer(playerName);
      setPlayerDetails(response.data);
      
      // Store the rating from averaged data
      setBaseRating(response.data.stats?.Rating || null);
      
      // Store which seasons this player actually has data for
      setPlayerAvailableSeasons(response.data.available_seasons || []);
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
      
      // Fetch data for the selected season (or averaged if null)
      const response = await getPlayer(currentPlayerName, season);
      
      // If viewing a specific season, ensure rating stays from averaged data
      if (season !== null && baseRating !== null) {
        response.data.stats.Rating = baseRating;
      }
      
      setPlayerDetails(response.data);
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
    setPlayerGrade(null);
  };

  return {
    playerDetails,
    loadingDetails,
    availableSeasons: playerAvailableSeasons,
    currentSeason,
    playerGrade,
    handlePlayerClick,
    handleSeasonChange,
    closeDetails
  };
}
