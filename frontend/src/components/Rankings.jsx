/* Player rankings display with format and position filters */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { getRankings } from '../api';
import PlayerDetailsModal from './PlayerDetailsModal';
import { usePlayerDetails } from '../hooks/usePlayerDetails';
import { getPlayerName } from '../utils/helpers';
import { LoadingMessage, ErrorMessage, EmptyStateMessage, PlayerTableRow } from './common';
import { getRatingValue, sortPlayersByRating } from '../utils/ratingHelpers';
import { TOP_N_OPTIONS } from '../utils/uiOptions';
import './Rankings.css';

export default function Rankings() {
  const [rankings, setRankings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [format, setFormat] = useState('redraft');
  const [position, setPosition] = useState(null);
  const [topN, setTopN] = useState(20);
  
  const { 
    playerDetails, 
    loadingDetails,
    availableSeasons,
    currentSeason,
    playerRankingData,
    handlePlayerClick,
    handleSeasonChange,
    closeDetails 
  } = usePlayerDetails();

  const fetchRankings = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getRankings(format, position);
      setRankings(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching rankings:', err);
    } finally {
      setLoading(false);
    }
  }, [format, position]);

  useEffect(() => {
    fetchRankings();
  }, [fetchRankings]);

  const sortedByPosition = useMemo(
    () =>
      Object.entries(rankings?.rankings || {}).map(([pos, players]) => ({
        pos,
        players: sortPlayersByRating(players, format).slice(0, topN),
      })),
    [rankings, format, topN]
  );

  const sortedOverallPlayers = useMemo(() => {
    const allPlayers = Object.entries(rankings?.rankings || {}).flatMap(([pos, players]) =>
      players.map((player) => ({
        ...player,
        position: pos,
        playerName: getPlayerName(player),
      }))
    );
    return sortPlayersByRating(allPlayers, format).slice(0, topN);
  }, [rankings, format, topN]);

  if (loading) return <LoadingMessage message="Loading rankings..." />;
  if (error) return <ErrorMessage message={error} />;
  if (!rankings) return <EmptyStateMessage message="No data available" />;

  const renderPlayerRow = (player, idx, showPosition = false) => {
    const playerName = showPosition ? player.playerName : getPlayerName(player);
    const ratingValue = getRatingValue(player, format);
    return (
      <PlayerTableRow
        key={playerName}
        player={{ ...player, playerName }}
        index={idx}
        ratingValue={ratingValue}
        showPosition={showPosition}
        onPlayerClick={handlePlayerClick}
      />
    );
  };

  const renderPositionTables = () =>
    sortedByPosition.map(({ pos, players }) => {
      return (
        <div key={pos} className="position-section">
          <h2>{pos}</h2>
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Age</th>
                <th>Rating</th>
              </tr>
            </thead>
            <tbody>
              {players.map((player, idx) => renderPlayerRow(player, idx))}
            </tbody>
          </table>
        </div>
      );
    });

  const renderOverallTable = () => {
    return (
      <div className="position-section">
        <h2>Overall Rankings</h2>
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Player</th>
              <th>Position</th>
              <th>Age</th>
              <th>Rating</th>
            </tr>
          </thead>
          <tbody>
            {sortedOverallPlayers.map((player, idx) => renderPlayerRow(player, idx, true))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="rankings-container">
      <h1>Player Rankings</h1>
      
      <div className="methodology-explanation">
        <h3>How Ratings Are Calculated</h3>
        <p>
          Player ratings are generated using <strong>Ridge Regression</strong>, a machine learning model trained on historical performance data. 
          The model identifies key statistical patterns that correlate with fantasy success and assigns each player a rating score based on these patterns.
        </p>
        <p className="playoff-note">
          <strong>Note:</strong> Statistics include regular season games only.
        </p>
      </div>
      
      <div className="controls">
        <div className="control-group">
          <label>Format:</label>
          <select value={format} onChange={(e) => setFormat(e.target.value)}>
            <option value="redraft">Redraft</option>
            <option value="dynasty">Dynasty</option>
          </select>
        </div>

        <div className="control-group">
          <label>Position:</label>
          <select value={position || ''} onChange={(e) => setPosition(e.target.value || null)}>
            <option value="">Overall</option>
            <option value="QB">QB</option>
            <option value="RB">RB</option>
            <option value="WR">WR</option>
            <option value="TE">TE</option>
          </select>
        </div>

        <div className="control-group">
          <label>Show:</label>
          <select value={topN} onChange={(e) => setTopN(Number(e.target.value))}>
            {TOP_N_OPTIONS.map((n) => (
              <option key={n} value={n}>Top {n}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="rankings-table">
        {position ? renderPositionTables() : renderOverallTable()}
      </div>

      {(playerDetails || loadingDetails) && (
        <PlayerDetailsModal
          playerDetails={playerDetails}
          loading={loadingDetails}
          onClose={closeDetails}
          availableSeasons={availableSeasons}
          currentSeason={currentSeason}
          onSeasonChange={handleSeasonChange}
          rankingData={playerRankingData}
        />
      )}
    </div>
  );
}
