import PlayerDetailsModal from './PlayerDetailsModal';

/**
 * Reusable wrapper for rendering PlayerDetailsModal with player details hook state
 */
export default function PlayerDetailsModalWrapper({ 
  playerDetails,
  loadingDetails,
  availableSeasons,
  currentSeason,
  playerRankingData,
  onSeasonChange,
  closeDetails
}) {
  if (!playerDetails && !loadingDetails) return null;

  return (
    <PlayerDetailsModal 
      playerDetails={playerDetails}
      loading={loadingDetails}
      onClose={closeDetails}
      availableSeasons={availableSeasons}
      currentSeason={currentSeason}
      onSeasonChange={onSeasonChange}
      rankingData={playerRankingData}
    />
  );
}
