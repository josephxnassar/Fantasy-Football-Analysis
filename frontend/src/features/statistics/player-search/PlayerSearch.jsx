import { useState } from 'react';
import { searchPlayers } from '../../../api';
import { ErrorMessage, EmptyStateMessage, SelectablePlayerCard } from '../../../shared/ui';
import './PlayerSearch.css';

export default function PlayerSearch({onPlayerClick, className, heading = 'Search Players', maxResults, variant = 'default'}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  const results = searchResults?.results ?? [];
  const displayResults = maxResults ? results.slice(0, maxResults) : results;

  const containerClassName = ['player-search-container', `player-search--${variant}`, className].filter(Boolean).join(' ');

  return (
    <div className={containerClassName}>
      <div className="search-section">
        <h2 className="search-heading">{heading}</h2>
        <form onSubmit={handleSearch} className="search-form">
          <input type="text" placeholder="Search by player name..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="player-search-input"/>
          <button type="submit" className="search-button" disabled={loading}>{loading ? 'Searching...' : 'Search'}</button>
        </form>
        {error && <ErrorMessage message={error} />}
        {searchResults && (
          <div className="results-section">
            <h3 className="results-count">Found {searchResults.count} players</h3>
            {searchResults.count > 0 ? (
              <div className="results-grid">
                {displayResults.map((player) => <SelectablePlayerCard key={player.name} player={player} onPlayerClick={onPlayerClick} />)}
              </div>
            ) : (
            <EmptyStateMessage message={`No players found matching "${searchQuery}"`} />)}
          </div>
        )}
      </div>
    </div>
  );
}
