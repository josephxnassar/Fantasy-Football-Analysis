import { useMemo, useState } from 'react';
import { SubTabNav } from '../common';
import PlayerEfficiencyTab from './PlayerEfficiencyTab';
import PlayerFantasyTab from './PlayerFantasyTab';
import PlayerInterpretationTab from './PlayerInterpretationTab';
import PlayerOpportunityTab from './PlayerOpportunityTab';
import StatsSeasonSelector from './StatsSeasonSelector';
import StatsViewModeToggle from './StatsViewModeToggle';

const STATS_TABS = [
  { id: 'fantasy', label: 'Fantasy' },
  { id: 'opportunity', label: 'Role & Opportunity' },
  { id: 'efficiency', label: 'Efficiency' },
  { id: 'interpretation', label: 'Interpretation' },
];

const TAB_COMPONENTS = {
  fantasy: PlayerFantasyTab,
  opportunity: PlayerOpportunityTab,
  efficiency: PlayerEfficiencyTab,
  interpretation: PlayerInterpretationTab,
};

export default function PlayerStatsView({
  playerDetails,
  availableSeasons,
  onSeasonChange,
  currentSeason,
  viewMode,
  setViewMode,
}) {
  const [statsTab, setStatsTab] = useState('fantasy');
  const hasWeeklyData = useMemo(
    () => Array.isArray(playerDetails?.weekly_stats) && playerDetails.weekly_stats.length > 0,
    [playerDetails]
  );
  const ActiveTabComponent = TAB_COMPONENTS[statsTab] || PlayerFantasyTab;

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
        playerDetails={playerDetails}
        currentSeason={currentSeason}
        viewMode={viewMode}
      />
    </>
  );
}
