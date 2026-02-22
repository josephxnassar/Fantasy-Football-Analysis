import { useState } from 'react';
import { SubTabNav } from '../common';
import PlayerEfficiencyTab from './PlayerEfficiencyTab';
import PlayerFantasyTab from './PlayerFantasyTab';
import PlayerInterpretationTab from './PlayerInterpretationTab';
import PlayerOpportunityTab from './PlayerOpportunityTab';
import StatsSeasonSelector from './StatsSeasonSelector';
import StatsViewModeToggle from './StatsViewModeToggle';

const STAT_TAB_CONFIG = [
  { id: 'fantasy', label: 'Fantasy', component: PlayerFantasyTab },
  { id: 'opportunity', label: 'Role & Opportunity', component: PlayerOpportunityTab },
  { id: 'efficiency', label: 'Efficiency', component: PlayerEfficiencyTab },
  { id: 'interpretation', label: 'Interpretation', component: PlayerInterpretationTab },
];

const STATS_TABS = STAT_TAB_CONFIG.map(({ id, label }) => ({ id, label }));

export default function PlayerStatsView({
  playerDetails,
  seasonControls,
}) {
  const [viewMode, setViewMode] = useState('aggregate');
  const [statsTab, setStatsTab] = useState('fantasy');
  const { availableSeasons, currentSeason, onSeasonChange } = seasonControls;
  const hasWeeklyData = Array.isArray(playerDetails?.weekly_stats) && playerDetails.weekly_stats.length > 0;
  const ActiveTabComponent = STAT_TAB_CONFIG.find((tab) => tab.id === statsTab)?.component || PlayerFantasyTab;
  const statsContext = { playerDetails, currentSeason, viewMode };

  return (
    <>
      <StatsSeasonSelector
        availableSeasons={availableSeasons}
        currentSeason={currentSeason}
        onSeasonChange={onSeasonChange}
      />

      <StatsViewModeToggle
        viewMode={viewMode}
        setViewMode={setViewMode}
        hasWeeklyData={hasWeeklyData}
      />

      <div className="player-stats-tab-nav">
        <SubTabNav
          tabs={STATS_TABS}
          activeTab={statsTab}
          onTabChange={setStatsTab}
        />
      </div>

      <ActiveTabComponent
        statsContext={statsContext}
      />
    </>
  );
}
