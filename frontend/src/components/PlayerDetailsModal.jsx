/* Player details modal with stats and season selection */

import { useState } from 'react';
import { getTeamDepthChart } from '../api';
import { useTeamModalData } from '../hooks/useTeamModalData';
import { getTeamColor } from '../utils/teamColors';
import { ErrorMessage, ModalOverlay, SubTabNav } from './common';
import PlayerHeader from './player-details/PlayerHeader';
import PlayerOverviewTab from './player-details/PlayerOverviewTab';
import PlayerDepthChartTab from './player-details/PlayerDepthChartTab';
import StatsSeasonSelector from './player-details/StatsSeasonSelector';
import StatsViewModeToggle from './player-details/StatsViewModeToggle';
import './player-details/PlayerStats.css';
import './PlayerDetailsModal.css';

export default function PlayerDetailsModal({ 
  playerDetails, 
  loading, 
  error,
  onClose, 
  availableSeasons = [],
  onSeasonChange,
  currentSeason,
}) {
  // Local modal tab state: stats view or team depth-chart view.
  const [modalTab, setModalTab] = useState('statistics');
  const [viewMode, setViewMode] = useState('aggregate');

  // Depth chart is loaded on demand only when that tab is opened.
  const { data: teamDepthChart, loading: depthChartLoading, error: depthChartError } = useTeamModalData(
    modalTab === 'depth-chart' ? playerDetails?.team : null,
    getTeamDepthChart,
    'Failed to load depth chart'
  );
  const playerTeamColor = getTeamColor(playerDetails?.team);
  const playerModalStyle = {
    '--player-team-color': playerTeamColor,
    '--player-team-tint': `${playerTeamColor}10`,
    '--player-team-border': `${playerTeamColor}38`,
    '--player-team-chip': `${playerTeamColor}14`,
  };
  const hasWeeklyData = Array.isArray(playerDetails?.weekly_stats) && playerDetails.weekly_stats.length > 0;
  const showStatsActions = modalTab === 'statistics' && (availableSeasons.length > 1 || hasWeeklyData);

  if (!playerDetails && !loading && !error) return null;

  return (
    <ModalOverlay className="modal-overlay--player-details" onClose={onClose}>
      <div className="player-details-modal-content" style={playerModalStyle}>
        {loading ? (
          <div className="loading">Loading player details...</div>
        ) : (
          <>
            {error && <ErrorMessage message={error} />}

            {playerDetails ? (
              <div className="player-dashboard">
                <div className="player-dashboard-header">
                  <PlayerHeader playerDetails={playerDetails} />

                  <div className="player-dashboard-tabs">
                    <SubTabNav
                      tabs={[
                        { id: 'statistics', label: 'Statistics' },
                        { id: 'depth-chart', label: 'Depth Chart' },
                      ]}
                      activeTab={modalTab}
                      onTabChange={setModalTab}
                      variant="compact"
                    />
                  </div>

                  {showStatsActions && (
                    <div className="player-dashboard-controls">
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
                    </div>
                  )}

                  <button
                    className="player-details-close-button"
                    onClick={onClose}
                    aria-label="Close player details"
                  >
                    ×
                  </button>
                </div>

                <div className="player-details-body">
                  {modalTab === 'statistics' && (
                    <PlayerOverviewTab
                      statsContext={{ playerDetails, currentSeason, viewMode }}
                    />
                  )}

                  {modalTab === 'depth-chart' && (
                    <PlayerDepthChartTab
                      depthChartLoading={depthChartLoading}
                      depthChartError={depthChartError}
                      teamDepthChart={teamDepthChart}
                      playerName={playerDetails?.name}
                    />
                  )}
                </div>
              </div>
            ) : (
              <p className="player-details-no-data">No player details available.</p>
            )}
          </>
        )}
      </div>
    </ModalOverlay>
  );
}
