/* Player details modal with stats and season selection */

import { useState } from 'react';
import { useTeamDepthChart } from '../hooks/useTeamDepthChart';
import { SubTabNav } from './common';
import PlayerHeader from './player-details/PlayerHeader';
import PlayerStatsView from './player-details/PlayerStatsView';
import PlayerDepthChartTab from './player-details/PlayerDepthChartTab';
import './PlayerDetailsModal.css';

export default function PlayerDetailsModal({ 
  playerDetails, 
  loading, 
  onClose, 
  availableSeasons = [],
  onSeasonChange,
  currentSeason
}) {
  const [modalTab, setModalTab] = useState('statistics'); // 'statistics' or 'depth-chart'
  const { teamDepthChart, depthChartLoading } = useTeamDepthChart(playerDetails?.team);

  if (!playerDetails && !loading) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="player-details-close-button" onClick={onClose}>×</button>
        
        {loading ? (
          <div className="loading">Loading player details...</div>
        ) : (
          <>
            <PlayerHeader playerDetails={playerDetails} />
            <div className="player-details">
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
                  teamDepthChart={teamDepthChart}
                  playerName={playerDetails?.name}
                />
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
