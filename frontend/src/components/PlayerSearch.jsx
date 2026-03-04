/* Reusable player search form with results grid */

import { useState } from 'react';
import { searchPlayers } from '../api';
import { ErrorMessage, EmptyStateMessage, PlayerCard } from './common';
import './PlayerSearch.css';

/**
 * @param {Object} props
 * @param {Function} props.onPlayerClick — called with player name when a result is clicked
 * @param {string}  [props.className]   — optional wrapper class for context-specific styling
 * @param {string}  [props.heading]     — section heading (default: "Search Players")
 * @param {number}  [props.maxResults]  — cap displayed results (default: show all)
 */
export default function PlayerSearch({ onPlayerClick, className, heading = 'Search Players', maxResults }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Execute player search and update result/error state.
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

  const displayResults = searchResults?.results && maxResults
    ? searchResults.results.slice(0, maxResults)
    : searchResults?.results;

  return (
    <div className={`player-search-container ${className || ''}`}>
      <div className="search-section">
        <h2>{heading}</h2>
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
                {displayResults.map((player) => (
                  <PlayerCard
                    key={player.name}
                    player={player}
                    onPlayerClick={onPlayerClick}
                  />
                ))}
              </div>
            ) : (
              <EmptyStateMessage message={`No players found matching "${searchQuery}"`} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
