import { useState } from 'react';
import { getPlayer } from '../api';

export function usePlayerDetails() {
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [playerDetails, setPlayerDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [error, setError] = useState(null);

  const handlePlayerClick = async (playerName) => {
    try {
      setLoadingDetails(true);
      setSelectedPlayer(playerName);
      setError(null);
      const response = await getPlayer(playerName);
      setPlayerDetails(response.data);
    } catch (err) {
      setError(`Failed to load player details: ${err.message}`);
    } finally {
      setLoadingDetails(false);
    }
  };

  const closeDetails = () => {
    setPlayerDetails(null);
    setSelectedPlayer(null);
    setError(null);
  };

  return {
    selectedPlayer,
    playerDetails,
    loadingDetails,
    error,
    handlePlayerClick,
    closeDetails
  };
}
