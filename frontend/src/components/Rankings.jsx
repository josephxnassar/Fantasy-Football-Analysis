import React, { useState, useEffect } from 'react';
import { getRankings, getPlayer } from '../api';
import './Rankings.css';

export default function Rankings() {
  const [rankings, setRankings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [format, setFormat] = useState('redraft');
  const [position, setPosition] = useState(null);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [playerDetails, setPlayerDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  useEffect(() => {
    fetchRankings();
  }, [format, position]);

  const fetchRankings = async () => {
    try {
      setLoading(true);
      const response = await getRankings(format, position, 'ridge');
      setRankings(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching rankings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePlayerClick = async (playerName) => {
    try {
      setLoadingDetails(true);
      setSelectedPlayer(playerName);
      console.log('Clicked player:', playerName);
      const response = await getPlayer(playerName);
      console.log('Player details response:', response.data);
      setPlayerDetails(response.data);
    } catch (err) {
      console.error('Error loading player:', err);
      setError(`Failed to load player details: ${err.message}`);
    } finally {
      setLoadingDetails(false);
    }
  };

  const closeDetails = () => {
    setPlayerDetails(null);
    setSelectedPlayer(null);
  };

  if (loading) return <div className="loading">Loading rankings...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!rankings) return <div className="error">No data available</div>;

  return (
    <div className="rankings-container">
      <h1>Player Rankings</h1>
      
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
            <option value="">All Positions</option>
            <option value="QB">QB</option>
            <option value="RB">RB</option>
            <option value="WR">WR</option>
            <option value="TE">TE</option>
          </select>
        </div>
      </div>

      <div className="rankings-table">
        {rankings.rankings && Object.entries(rankings.rankings).map(([pos, players]) => (
          <div key={pos} className="position-section">
            <h2>{pos}</h2>
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Player</th>
                  <th>Percentile</th>
                </tr>
              </thead>
              <tbody>
                {players.map((player, idx) => (
                  <tr key={idx}>
                    <td>{idx + 1}</td>
                    <td>
                      <span 
                        className="player-name-link"
                        onClick={() => handlePlayerClick(player.name || player[Object.keys(player)[0]])}
                      >
                        {player.name || player[Object.keys(player)[0]]}
                      </span>
                    </td>
                    <td>{typeof player.percentile === 'number' ? `${Math.round(player.percentile)}%` : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>

      {playerDetails && (
        <div className="modal-overlay" onClick={closeDetails}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-button" onClick={closeDetails}>×</button>
            
            {loadingDetails ? (
              <div className="loading">Loading player details...</div>
            ) : (
              <>
                <h2>{playerDetails.name}</h2>
                <div className="player-details">
                  <div className="details-grid">
                    <div className="detail-item">
                      <span className="label">Position:</span>
                      <span className="value">{playerDetails.position}</span>
                    </div>
                    <div className="detail-item">
                      <span className="label">Team:</span>
                      <span className="value">{playerDetails.team || 'N/A'}</span>
                    </div>
                  </div>

                  <div className="stats-section">
                    <h3>Stats</h3>
                    <div className="stats-grid">
                      {Object.entries(playerDetails.stats).map(([key, value]) => (
                        <div key={key} className="stat-item">
                          <span className="stat-label">{key}:</span>
                          <span className="stat-value">
                            {typeof value === 'number' ? value.toFixed(2) : value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {playerDetails.schedule && playerDetails.schedule.length > 0 && (
                    <div className="schedule-section">
                      <h3>Upcoming Schedule</h3>
                      <div className="schedule-list">
                        {playerDetails.schedule.map((game, idx) => (
                          <div key={idx} className="schedule-item">
                            <span className="week">Week {game.week}</span>
                            <span className="opponent">vs {game.opponent}</span>
                            {game.matchup_quality && (
                              <span className={`matchup-quality quality-${game.matchup_quality}`}>
                                {game.matchup_quality.toUpperCase()}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
