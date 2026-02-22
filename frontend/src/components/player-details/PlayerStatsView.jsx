import { useMemo, useState } from 'react';
import { SubTabNav } from '../common';
import PlayerEfficiencyTab from './PlayerEfficiencyTab';
import PlayerFantasyTab from './PlayerFantasyTab';
import PlayerInterpretationTab from './PlayerInterpretationTab';
import PlayerOpportunityTab from './PlayerOpportunityTab';

const STATS_TABS = [
  { id: 'fantasy', label: 'Fantasy' },
  { id: 'opportunity', label: 'Role & Opportunity' },
  { id: 'efficiency', label: 'Efficiency' },
  { id: 'interpretation', label: 'Interpretation' },
];

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

  return (
    <>
      {availableSeasons.length > 1 && (
        <div className="year-selector">
          <span className="year-label">View Stats:</span>
          <div className="year-buttons">
            {availableSeasons.map((season) => (
              <button
                key={season}
                className={`year-button ${currentSeason === season ? 'active' : ''}`}
                onClick={() => onSeasonChange(season)}
              >
                {season}
              </button>
            ))}
          </div>
        </div>
      )}

      {hasWeeklyData && (
        <div className="view-mode-toggle">
          <button
            className={`toggle-btn ${viewMode === 'aggregate' ? 'active' : ''}`}
            onClick={() => setViewMode('aggregate')}
          >
            Season Total
          </button>
          <button
            className={`toggle-btn ${viewMode === 'weekly' ? 'active' : ''}`}
            onClick={() => setViewMode('weekly')}
          >
            By Week
          </button>
        </div>
      )}

      <div className="player-stats-tab-nav">
        <SubTabNav
          tabs={STATS_TABS}
          activeTab={statsTab}
          onTabChange={setStatsTab}
        />
      </div>

      {statsTab === 'fantasy' && (
        <PlayerFantasyTab
          playerDetails={playerDetails}
          currentSeason={currentSeason}
          viewMode={viewMode}
        />
      )}
      {statsTab === 'opportunity' && (
        <PlayerOpportunityTab
          playerDetails={playerDetails}
          currentSeason={currentSeason}
          viewMode={viewMode}
        />
      )}
      {statsTab === 'efficiency' && (
        <PlayerEfficiencyTab
          playerDetails={playerDetails}
          currentSeason={currentSeason}
          viewMode={viewMode}
        />
      )}
      {statsTab === 'interpretation' && (
        <PlayerInterpretationTab
          playerDetails={playerDetails}
          currentSeason={currentSeason}
          viewMode={viewMode}
        />
      )}
    </>
  );
}
