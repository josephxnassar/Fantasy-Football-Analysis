/* Quick player search bar with inline results on the landing page */

import { useState } from 'react';
import { searchPlayers } from '../../api';
import { PlayerCard } from '../common';
import './QuickSearch.css';

export default function QuickSearch({ onPlayerClick }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [searching, setSearching] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (trimmed.length < 2) return;
    try {
      setSearching(true);
      const response = await searchPlayers(trimmed);
      setResults(response.data);
    } catch {
      setResults(null);
    } finally {
      setSearching(false);
    }
  };

  return (
    <section className="landing-section landing-search-section">
      <h2 className="section-heading">Quick Player Search</h2>
      <form className="landing-search-form" onSubmit={handleSearch}>
        <input
          type="text"
          className="landing-search-input"
          placeholder="Search by player name..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="landing-search-button" disabled={searching}>
          {searching ? 'Searching...' : 'Search'}
        </button>
      </form>
      {results && results.count > 0 && (
        <div className="landing-search-results">
          {results.results.slice(0, 6).map((player) => (
            <PlayerCard key={player.name} player={player} onPlayerClick={onPlayerClick} />
          ))}
        </div>
      )}
      {results && results.count === 0 && (
        <p className="landing-search-empty">No players found matching &quot;{query}&quot;</p>
      )}
    </section>
  );
}
