import { memo, useState, useMemo, useEffect, useCallback } from 'react';
import './DivisionBrowser.css';

function DivisionBrowser({ divisions, teamNames, loading, error, onTeamSelect, actionLabel = 'View Details →' }) {
  const [expandedConference, setExpandedConference] = useState('AFC');
  const [expandedDivision, setExpandedDivision] = useState('North');

  const conferences = useMemo(() => Object.keys(divisions || {}), [divisions]);
  const currentDivisions = useMemo(
    () => divisions?.[expandedConference] || {},
    [divisions, expandedConference]
  );
  const divisionNames = useMemo(() => Object.keys(currentDivisions), [currentDivisions]);
  const teams = useMemo(() => currentDivisions[expandedDivision] || [], [currentDivisions, expandedDivision]);

  useEffect(() => {
    if (conferences.length === 0) {
      return;
    }
    if (!conferences.includes(expandedConference)) {
      setExpandedConference(conferences[0]);
    }
  }, [conferences, expandedConference]);

  useEffect(() => {
    if (divisionNames.length === 0) {
      return;
    }
    if (!divisionNames.includes(expandedDivision)) {
      setExpandedDivision(divisionNames[0]);
    }
  }, [divisionNames, expandedDivision]);

  const handleConferenceSelect = useCallback(
    (conf) => {
      setExpandedConference(conf);
      const nextDivisions = divisions?.[conf] || {};
      const nextDivisionNames = Object.keys(nextDivisions);
      setExpandedDivision(nextDivisionNames[0] || 'North');
    },
    [divisions]
  );

  const handleDivisionSelect = useCallback((div) => {
    setExpandedDivision(div);
  }, []);

  const handleTeamSelect = useCallback(
    (team) => {
      onTeamSelect(team);
    },
    [onTeamSelect]
  );

  if (loading) {
    return <div className="loading">Loading divisions...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="division-browser">
      {/* Conference Selection */}
      <div className="conference-selector">
        {conferences.map((conf) => (
          <button
            key={conf}
            className={`conference-button ${expandedConference === conf ? 'active' : ''} ${conf.toLowerCase()}`}
            onClick={() => handleConferenceSelect(conf)}
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
            onClick={() => handleDivisionSelect(div)}
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
            onClick={() => handleTeamSelect(team)}
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

export default memo(DivisionBrowser);
