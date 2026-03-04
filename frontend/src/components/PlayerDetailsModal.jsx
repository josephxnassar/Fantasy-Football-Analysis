/* Player details modal with stats and season selection */

import { useState } from 'react';
import { getTeamDepthChart } from '../api';
import { useTeamModalData } from '../hooks/useTeamModalData';
import { ErrorMessage, ModalOverlay, SubTabNav } from './common';
import PlayerHeader from './player-details/PlayerHeader';
import PlayerStatsView from './player-details/PlayerStatsView';
import PlayerDepthChartTab from './player-details/PlayerDepthChartTab';
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

  // Depth chart is loaded on demand only when that tab is opened.
  const { data: teamDepthChart, loading: depthChartLoading, error: depthChartError } = useTeamModalData(
    modalTab === 'depth-chart' ? playerDetails?.team : null,
    getTeamDepthChart,
    'Failed to load depth chart'
  );

  if (!playerDetails && !loading && !error) return null;

  return (
    <ModalOverlay onClose={onClose}>
      <div className="modal-content">
        <button className="player-details-close-button" onClick={onClose}>×</button>

        {loading ? (
          <div className="loading">Loading player details...</div>
        ) : (
          <>
            {error && <ErrorMessage message={error} />}

            {playerDetails ? (
              <>
                <PlayerHeader playerDetails={playerDetails} />
                <div className="player-details">
                  {/* Top-level content tabs inside the player modal. */}
                  <SubTabNav
                    tabs={[
                      { id: 'statistics', label: 'Statistics' },
                      { id: 'depth-chart', label: 'Depth Chart' },
                    ]}
                    activeTab={modalTab}
                    onTabChange={setModalTab}
                  />

                  {modalTab === 'statistics' && (
                    <PlayerStatsView
                      playerDetails={playerDetails}
                      seasonControls={{
                        availableSeasons,
                        onSeasonChange,
                        currentSeason,
                      }}
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
              </>
            ) : (
              <p className="player-details-no-data">No player details available.</p>
            )}
          </>
        )}
      </div>
    </ModalOverlay>
  );
}
