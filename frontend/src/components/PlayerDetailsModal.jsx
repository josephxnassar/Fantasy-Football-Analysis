/* Player details modal with stats and season selection */

import { useState } from 'react';
import { useTeamDepthChart } from '../hooks/useTeamDepthChart';
import { SubTabNav } from './common';
import PlayerHeader from './player-details/PlayerHeader';
import PlayerRatings from './player-details/PlayerRatings';
import PlayerStatsView from './player-details/PlayerStatsView';
import PlayerDepthChartTab from './player-details/PlayerDepthChartTab';
import './PlayerDetailsModal.css';

export default function PlayerDetailsModal({ 
  playerDetails, 
  loading, 
  onClose, 
  availableSeasons = [],
  onSeasonChange,
  currentSeason,
  rankingData = null
}) {
  const [viewMode, setViewMode] = useState('aggregate'); // 'aggregate' or 'weekly'
  const [modalTab, setModalTab] = useState('statistics'); // 'statistics' or 'depth-chart'
  const { teamDepthChart, depthChartLoading } = useTeamDepthChart(playerDetails?.team);

  if (!playerDetails && !loading) return null;

  const rating = playerDetails?.stats?.redraft_rating;
  const dynastyRating = rankingData?.dynasty_rating;
  const posRankRedraft = rankingData?.pos_rank_redraft;
  const posRankDynasty = rankingData?.pos_rank_dynasty;
  const overallRankRedraft = rankingData?.overall_rank_redraft;
  const overallRankDynasty = rankingData?.overall_rank_dynasty;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        
        {loading ? (
          <div className="loading">Loading player details...</div>
        ) : (
          <>
            <PlayerHeader playerDetails={playerDetails} rankingData={rankingData} />
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
                <>
                  <PlayerRatings
                    rating={rating}
                    dynastyRating={dynastyRating}
                    position={playerDetails?.position}
                    posRankRedraft={posRankRedraft}
                    posRankDynasty={posRankDynasty}
                    overallRankRedraft={overallRankRedraft}
                    overallRankDynasty={overallRankDynasty}
                    isEligible={rankingData?.is_eligible ?? true}
                  />
                  <PlayerStatsView
                    playerDetails={playerDetails}
                    availableSeasons={availableSeasons}
                    onSeasonChange={onSeasonChange}
                    currentSeason={currentSeason}
                    viewMode={viewMode}
                    setViewMode={setViewMode}
                  />
                </>
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
