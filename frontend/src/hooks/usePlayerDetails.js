import { useState } from 'react';
import { getPlayer } from '../api';

export function usePlayerDetails() {
  const [playerDetails, setPlayerDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  const handlePlayerClick = async (playerName) => {
    try {
      setLoadingDetails(true);
      const response = await getPlayer(playerName);
      setPlayerDetails(response.data);
    } catch (err) {
      console.error(`Failed to load player details: ${err.message}`);
    } finally {
      setLoadingDetails(false);
    }
  };

  const closeDetails = () => {
    setPlayerDetails(null);
  };

  return {
    playerDetails,
    loadingDetails,
    handlePlayerClick,
    closeDetails
  };
}
