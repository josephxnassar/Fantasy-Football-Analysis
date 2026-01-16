import React, { useState } from 'react';
import { searchPlayers, getPlayer } from '../api';
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
                {searchResults.results.map((player, idx) => (
                  <div
                    key={idx}
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

      {playerDetails && (
        <div className="modal-overlay" onClick={closeDetails}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-button" onClick={closeDetails}>×</button>
            
            {loadingDetails ? (
              <div className="loading">Loading player details...</div>
            ) : (
              <>
                <h2>{playerDetails.name}</h2>
                <div className="player-details">
                  <div className="details-grid">
                    <div className="detail-item">
                      <span className="label">Position:</span>
                      <span className="value">{playerDetails.position}</span>
                    </div>
                    <div className="detail-item">
                      <span className="label">Team:</span>
                      <span className="value">{playerDetails.team || 'N/A'}</span>
                    </div>
                  </div>

                  <div className="stats-section">
                    <h3>Stats</h3>
                    <div className="stats-grid">
                      {Object.entries(playerDetails.stats).map(([key, value]) => (
                        <div key={key} className="stat-item">
                          <span className="stat-label">{key}:</span>
                          <span className="stat-value">
                            {typeof value === 'number' ? value.toFixed(2) : value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {playerDetails.schedule && playerDetails.schedule.length > 0 && (
                    <div className="schedule-section">
                      <h3>Upcoming Schedule</h3>
                      <div className="schedule-list">
                        {playerDetails.schedule.map((game, idx) => (
                          <div key={idx} className="schedule-item">
                            <span className="week">Week {game.week}</span>
                            <span className="opponent">vs {game.opponent}</span>
                            {game.matchup_quality && (
                              <span className={`matchup-quality quality-${game.matchup_quality}`}>
                                {game.matchup_quality.toUpperCase()}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
