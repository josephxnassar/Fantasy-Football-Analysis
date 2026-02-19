/* Player search component with live results */

import { useState } from 'react';
import { searchPlayers } from '../api';
import PlayerDetailsModal from './PlayerDetailsModal';
import { usePlayerDetails } from '../hooks/usePlayerDetails';
import { ErrorMessage, EmptyStateMessage, PlayerCard } from './common';
import './PlayerSearch.css';

export default function PlayerSearch() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const { 
    playerDetails, 
    loadingDetails,
    availableSeasons,
    currentSeason,
    playerRankingData,
    handlePlayerClick,
    handleSeasonChange,
    closeDetails 
  } = usePlayerDetails();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim() || searchQuery.length < 2) {
      setError('Please enter at least 2 characters');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await searchPlayers(searchQuery);
      setSearchResults(response.data);
    } catch (err) {
      setError(`Search failed: ${err.message}`);
      console.error('Error searching:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="player-search-container">
      <div className="search-section">
        <h2>Search Players</h2>
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Search by player name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="player-search-input"
          />
          <button type="submit" className="search-button" disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>

        {error && <ErrorMessage message={error} />}

        {searchResults && (
          <div className="results-section">
            <h3>Found {searchResults.count} players</h3>
            {searchResults.count > 0 ? (
              <div className="results-grid">
                {searchResults.results.map((player) => (
                  <PlayerCard
                    key={player.name}
                    player={player}
                    onPlayerClick={handlePlayerClick}
                  />
                ))}
              </div>
            ) : (
              <EmptyStateMessage message={`No players found matching "${searchQuery}"`} />
            )}
          </div>
        )}
      </div>

      {(playerDetails || loadingDetails) && (
        <PlayerDetailsModal
          playerDetails={playerDetails}
          loading={loadingDetails}
          onClose={closeDetails}
          availableSeasons={availableSeasons}
          currentSeason={currentSeason}
          onSeasonChange={handleSeasonChange}
          rankingData={playerRankingData}
        />
      )}
    </div>
  );
}
