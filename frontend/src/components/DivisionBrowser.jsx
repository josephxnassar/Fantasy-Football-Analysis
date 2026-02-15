import { useState } from 'react';
import './DivisionBrowser.css';

function DivisionBrowser({ divisions, teamNames, loading, error, onTeamSelect, actionLabel = 'View Details →' }) {
  const [expandedConference, setExpandedConference] = useState('AFC');
  const [expandedDivision, setExpandedDivision] = useState('North');

  if (loading) {
    return <div className="loading">Loading divisions...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  const conferences = Object.keys(divisions || {});
  const currentDivisions = divisions?.[expandedConference] || {};
  const divisionNames = Object.keys(currentDivisions);
  const teams = currentDivisions[expandedDivision] || [];

  return (
    <div className="division-browser">
      {/* Conference Selection */}
      <div className="conference-selector">
        {conferences.map((conf) => (
          <button
            key={conf}
            className={`conference-button ${expandedConference === conf ? 'active' : ''} ${conf.toLowerCase()}`}
            onClick={() => {
              setExpandedConference(conf);
              setExpandedDivision('North');
            }}
          >
            {conf}
          </button>
        ))}
      </div>

      {/* Division Selection */}
      <div className="division-selector">
        {divisionNames.map((div) => (
          <button
            key={div}
            className={`division-button ${expandedDivision === div ? 'active' : ''}`}
            onClick={() => setExpandedDivision(div)}
          >
            {div}
          </button>
        ))}
      </div>

      {/* Team Cards */}
      <div className="team-grid">
        {teams.map((team) => (
          <div
            key={team}
            className="team-card"
            onClick={() => onTeamSelect(team)}
          >
            <div className="team-abbr">{team}</div>
            <div className="team-name">{teamNames[team] || team}</div>
            <div className="team-action">{actionLabel}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DivisionBrowser;
