import React, { useState } from 'react';
import { searchPlayers, getPlayer } from '../api';
import PlayerDetailsModal from './PlayerDetailsModal';
import './PlayerSearch.css';

export default function PlayerSearch() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [playerDetails, setPlayerDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

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

  const handlePlayerClick = async (playerName) => {
    try {
      setLoadingDetails(true);
      setSelectedPlayer(playerName);
      const response = await getPlayer(playerName);
      setPlayerDetails(response.data);
    } catch (err) {
      setError(`Failed to load player details: ${err.message}`);
      console.error('Error loading player:', err);
    } finally {
      setLoadingDetails(false);
    }
  };

  const closeDetails = () => {
    setPlayerDetails(null);
    setSelectedPlayer(null);
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
            className="search-input"
          />
          <button type="submit" className="search-button" disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        {searchResults && (
          <div className="results-section">
            <h3>Found {searchResults.count} players</h3>
            {searchResults.count > 0 ? (
              <div className="results-grid">
                {searchResults.results.map((player) => (
                  <div
                    key={player.name}
                    className="player-card"
                    onClick={() => handlePlayerClick(player.name)}
                  >
                    <div className="player-name">{player.name}</div>
                    <div className="player-info">
                      <span className="position-badge">{player.position}</span>
                      <span className="rating">Rating: {player.rating.toFixed(2)}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-results">No players found matching "{searchQuery}"</p>
            )}
          </div>
        )}
      </div>

      {(playerDetails || loadingDetails) && (
        <PlayerDetailsModal 
          playerDetails={playerDetails}
          loading={loadingDetails}
          onClose={closeDetails}
        />
      )}
    </div>
  );
}
