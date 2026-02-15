import { useState } from 'react';
import './TeamSearch.css';

function TeamSearch({ allTeams, teamNames, loading, error, onTeamSelect }) {
  const [query, setQuery] = useState('');

  const filteredTeams = allTeams.filter((team) => {
    const searchLower = query.toLowerCase();
    const teamNameLower = (teamNames[team] || '').toLowerCase();
    return (
      team.toLowerCase().includes(searchLower) ||
      teamNameLower.includes(searchLower)
    );
  });

  if (loading) {
    return <div className="loading">Loading teams...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="team-search">
      <div className="search-container">
        <input
          type="text"
          className="search-input"
          placeholder="Search teams by name or abbreviation..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        {query && (
          <button className="clear-button" onClick={() => setQuery('')}>
            ×
          </button>
        )}
      </div>

      <div className="teams-list">
        {filteredTeams.length === 0 && query && (
          <div className="empty-state">No teams found matching "{query}"</div>
        )}
        
        {filteredTeams.map((team) => (
          <div
            key={team}
            className="team-item"
            onClick={() => onTeamSelect(team)}
          >
            <span className="team-item-abbr">{team}</span>
            <span className="team-item-name">{teamNames[team] || team}</span>
            <span className="team-item-arrow">→</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TeamSearch;
