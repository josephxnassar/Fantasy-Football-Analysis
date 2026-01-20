import { useState, useEffect, useCallback } from 'react';
import { getRankings } from '../api';
import PlayerDetailsModalWrapper from './PlayerDetailsModalWrapper';
import { usePlayerDetails } from '../hooks/usePlayerDetails';
import { getPlayerName } from '../utils/helpers';
import './Rankings.css';

export default function Rankings() {
  const [rankings, setRankings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [format, setFormat] = useState('redraft');
  const [position, setPosition] = useState(null);
  
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

  if (loading) return <div className="loading">Loading rankings...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!rankings) return <div className="error">No data available</div>;

  const renderPlayerRow = (player, idx, showPosition = false) => {
    const playerName = showPosition ? player.playerName : getPlayerName(player);
    const rating = format === 'dynasty' 
      ? (typeof player.DynastyRating === 'number' ? player.DynastyRating.toFixed(2) : 'N/A')
      : (typeof player.Rating === 'number' ? player.Rating.toFixed(2) : 'N/A');
    return (
      <tr key={playerName}>
        <td>{idx + 1}</td>
        <td>
          <span className="player-name-link" onClick={() => handlePlayerClick(playerName, player)}>
            {playerName}
          </span>
        </td>
        {showPosition && <td>{player.position}</td>}
        <td>{rating}</td>
      </tr>
    );
  };

  const renderPositionTables = () => 
    Object.entries(rankings.rankings).map(([pos, players]) => (
      <div key={pos} className="position-section">
        <h2>{pos}</h2>
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Player</th>
              <th>Rating</th>
            </tr>
          </thead>
          <tbody>
            {players.map((player, idx) => renderPlayerRow(player, idx))}
          </tbody>
        </table>
      </div>
    ));

  const renderOverallTable = () => {
    const allPlayers = Object.entries(rankings.rankings).flatMap(([pos, players]) =>
      players.map(player => ({
        ...player,
        position: pos,
        playerName: getPlayerName(player)
      }))
    );
    
    const ratingField = format === 'dynasty' ? 'DynastyRating' : 'Rating';
    allPlayers.sort((a, b) => (b[ratingField] || 0) - (a[ratingField] || 0));
    
    return (
      <div className="position-section">
        <h2>Overall Rankings</h2>
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Player</th>
              <th>Position</th>
              <th>Rating</th>
            </tr>
          </thead>
          <tbody>
            {allPlayers.map((player, idx) => {
              const rating = format === 'dynasty'
                ? (typeof player.DynastyRating === 'number' ? player.DynastyRating.toFixed(2) : 'N/A')
                : (typeof player.Rating === 'number' ? player.Rating.toFixed(2) : 'N/A');
              return (
                <tr key={player.playerName}>
                  <td>{idx + 1}</td>
                  <td>
                    <span className="player-name-link" onClick={() => handlePlayerClick(player.playerName, player)}>
                      {player.playerName}
                    </span>
                  </td>
                  <td>{player.position}</td>
                  <td>{rating}</td>
                </tr>
              );
            })}
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
        <ul>
          <li><strong>Rating Score:</strong> A numerical score derived from statistical patterns in 2024 season data</li>
          <li><strong>Percentile:</strong> Shows where each player ranks relative to others (0-100%, where 100% = best)</li>
          <li><strong>Tier:</strong> Visual categorization based on percentile:
            <ul>
              <li>🟢 <strong>Elite</strong> (90%+) - Top tier performers</li>
              <li>🔵 <strong>Very Good</strong> (75-89%) - Strong performers</li>
              <li>🟡 <strong>Good</strong> (50-74%) - Above average</li>
              <li>🟠 <strong>Average</strong> (25-49%) - Average performers</li>
              <li>🔴 <strong>Below Average</strong> (&lt;25%) - Lower tier</li>
            </ul>
          </li>
        </ul>
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
      </div>

      <div className="rankings-table">
        {position ? renderPositionTables() : renderOverallTable()}
      </div>

      <PlayerDetailsModalWrapper
        playerDetails={playerDetails}
        loadingDetails={loadingDetails}
        availableSeasons={availableSeasons}
        currentSeason={currentSeason}
        playerRankingData={playerRankingData}
        onSeasonChange={handleSeasonChange}
        closeDetails={closeDetails}
      />
    </div>
  );
}
