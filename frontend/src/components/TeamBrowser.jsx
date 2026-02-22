/* Shared team browser component used by Schedules and Depth Charts tabs. Provides Division Browser / Team Search sub-tabs and renders a modal via renderModal prop. */

import { useState, useCallback } from 'react';
import DivisionBrowser from './DivisionBrowser';
import TeamSearch from './TeamSearch';
import { SubTabNav } from './common';
import { useDivisions } from '../hooks/useDivisions';
import './TeamBrowser.css';

const TABS = [
  { id: 'browse', label: 'Division Browser' },
  { id: 'search', label: 'Team Search' },
];

function TeamBrowser({ actionLabel, renderModal }) {
  // Sub-tab for browse vs search modes.
  const [activeSubTab, setActiveSubTab] = useState('browse');

  // Selected team controls modal visibility.
  const [selectedTeam, setSelectedTeam] = useState(null);

  // Shared teams/divisions payload used by both sub-tabs.
  const { divisions, teamNames, allTeams, loading, error } = useDivisions();

  const handleTeamSelect = useCallback((team) => {
    setSelectedTeam(team);
  }, []);

  const handleCloseModal = useCallback(() => {
    setSelectedTeam(null);
  }, []);

  return (
    <div className="team-browser-container">
      <SubTabNav tabs={TABS} activeTab={activeSubTab} onTabChange={setActiveSubTab} />

      <div className="team-browser-content">
        {activeSubTab === 'browse' ? (
          <DivisionBrowser
            divisions={divisions}
            teamNames={teamNames}
            loading={loading}
            error={error}
            onTeamSelect={handleTeamSelect}
            actionLabel={actionLabel}
          />
        ) : (
          <TeamSearch
            allTeams={allTeams}
            teamNames={teamNames}
            loading={loading}
            error={error}
            onTeamSelect={handleTeamSelect}
          />
        )}
      </div>

      {selectedTeam && renderModal(selectedTeam, handleCloseModal)}
    </div>
  );
}

export default TeamBrowser;
