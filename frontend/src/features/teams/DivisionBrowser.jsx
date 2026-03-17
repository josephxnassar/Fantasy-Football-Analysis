import { useState, useEffect } from 'react';
import { getTeamColorVars } from '../../shared/utils/teamColors';
import './DivisionBrowser.css';

function DivisionBrowser({
  divisions,
  teamNames,
  loading,
  error,
  onTeamSelect,
  actionLabel = 'View Details →',
  defaultConference = 'AFC',
  defaultDivision = 'North',
}) {
  const [expandedConference, setExpandedConference] = useState(defaultConference);
  const [expandedDivision, setExpandedDivision] = useState(defaultDivision);
  const conferences = Object.keys(divisions || {});
  const currentDivisions = divisions?.[expandedConference] || {};
  const divisionNames = Object.keys(currentDivisions);
  const teams = currentDivisions[expandedDivision] || [];

  useEffect(() => {
    if (conferences.length && !conferences.includes(expandedConference)) {
      setExpandedConference(conferences[0]);
    }
  }, [conferences, expandedConference]);

  useEffect(() => {
    if (divisionNames.length && !divisionNames.includes(expandedDivision)) {
      setExpandedDivision(divisionNames[0]);
    }
  }, [divisionNames, expandedDivision]);

  if (loading) return <div className="loading">Loading divisions...</div>;

  if (error) return <div className="error">{error}</div>;

  return (
    <div className="division-browser">
      <div className="conference-selector">
        {conferences.map((conf) => (
          <button
            key={conf}
            className={`conference-button ${expandedConference === conf ? 'active' : ''} ${conf.toLowerCase()}`}
            onClick={() => {
              setExpandedConference(conf);
              setExpandedDivision(Object.keys(divisions?.[conf] || {})[0] || 'North');
            }}
          >
            {conf}
          </button>
        ))}
      </div>

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

      <div className="team-grid">
        {teams.map((team) => (
          <button type="button" key={team} className="team-card" style={getTeamColorVars(team)} onClick={() => onTeamSelect(team)}>
            <div className="team-abbr">{team}</div>
            <div className="team-name">{teamNames[team] || team}</div>
            <div className="team-action">{actionLabel}</div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default DivisionBrowser;
