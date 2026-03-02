import { useState } from 'react';
import { SubTabNav } from '../common';
import PlayerAdvancedTab from './PlayerAdvancedTab';
import PlayerOverviewTab from './PlayerOverviewTab';
import './PlayerStats.css';
import PlayerUsageTab from './PlayerUsageTab';
import StatsSeasonSelector from './StatsSeasonSelector';
import StatsViewModeToggle from './StatsViewModeToggle';

const STAT_TAB_CONFIG = [
  { id: 'overview', label: 'Overview', component: PlayerOverviewTab },
  { id: 'usage', label: 'Usage', component: PlayerUsageTab },
  { id: 'advanced', label: 'Advanced', component: PlayerAdvancedTab },
];

const STATS_TABS = STAT_TAB_CONFIG.map(({ id, label }) => ({ id, label }));

export default function PlayerStatsView({
  playerDetails,
  seasonControls,
}) {
  // Aggregate = season rollup, weekly = week-by-week cards.
  const [viewMode, setViewMode] = useState('aggregate');

  // Active sub-tab inside the Statistics panel.
  const [statsTab, setStatsTab] = useState('overview');

  const { availableSeasons, currentSeason, onSeasonChange } = seasonControls;
  const hasWeeklyData = Array.isArray(playerDetails?.weekly_stats) && playerDetails.weekly_stats.length > 0;

  // Resolve current tab component from config (fallback keeps UI resilient).
  const ActiveTabComponent = STAT_TAB_CONFIG.find((tab) => tab.id === statsTab)?.component || PlayerOverviewTab;

  // Shared tab context passed through tab/layout stack.
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
