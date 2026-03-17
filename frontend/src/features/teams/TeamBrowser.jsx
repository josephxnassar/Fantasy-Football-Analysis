import { useState } from 'react';
import DivisionBrowser from './DivisionBrowser';
import TeamSearch from './TeamSearch';
import { SubTabNav } from '../../shared/ui';
import { useDivisions } from './useDivisions';
import './TeamBrowser.css';

const TABS = [
  { id: 'browse', label: 'Division Browser' },
  { id: 'search', label: 'Team Search' },
];

function TeamBrowser({ actionLabel, renderModal }) {
  const [activeSubTab, setActiveSubTab] = useState('browse');
  const [selectedTeam, setSelectedTeam] = useState(null);
  const { divisions, teamNames, allTeams, loading, error } = useDivisions();

  return (
    <div className="team-browser-container">
      <SubTabNav tabs={TABS} activeTab={activeSubTab} onTabChange={setActiveSubTab}/>

      <div className="team-browser-content">
        {activeSubTab === 'browse' ? (<DivisionBrowser divisions={divisions} teamNames={teamNames} loading={loading} error={error} onTeamSelect={setSelectedTeam} actionLabel={actionLabel}/>) : (<TeamSearch allTeams={allTeams} teamNames={teamNames} loading={loading} error={error} onTeamSelect={setSelectedTeam}/>)}
      </div>

      {selectedTeam && renderModal(selectedTeam, () => setSelectedTeam(null))}
    </div>
  );
}

export default TeamBrowser;
