import { useState } from 'react';
import PlayerOverviewTab from './PlayerOverviewTab';
import './PlayerStats.css';
import StatsSeasonSelector from './StatsSeasonSelector';
import StatsViewModeToggle from './StatsViewModeToggle';

export default function PlayerStatsView({
  playerDetails,
  seasonControls,
}) {
  // Aggregate = season rollup, weekly = week-by-week cards.
  const [viewMode, setViewMode] = useState('aggregate');

  const { availableSeasons, currentSeason, onSeasonChange } = seasonControls;
  const hasWeeklyData = Array.isArray(playerDetails?.weekly_stats) && playerDetails.weekly_stats.length > 0;

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

      <PlayerOverviewTab
        statsContext={statsContext}
      />
    </>
  );
}
