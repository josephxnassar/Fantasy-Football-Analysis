import React, { useState, useEffect } from 'react';
import { getRankings } from '../api';
import './Rankings.css';

export default function Rankings() {
  const [rankings, setRankings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [format, setFormat] = useState('redraft');
  const [position, setPosition] = useState(null);
  const [model, setModel] = useState('ridge');

  useEffect(() => {
    fetchRankings();
  }, [format, position, model]);

  const fetchRankings = async () => {
    try {
      setLoading(true);
      const response = await getRankings(format, position, model);
      setRankings(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching rankings:', err);
    } finally {
      setLoading(false);
    }
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

        <div className="control-group">
          <label>Model:</label>
          <select value={model} onChange={(e) => setModel(e.target.value)}>
            <option value="linear">Linear</option>
            <option value="ridge">Ridge</option>
            <option value="lasso">Lasso</option>
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
                  <th>Rating</th>
                </tr>
              </thead>
              <tbody>
                {players.map((player, idx) => (
                  <tr key={idx}>
                    <td>{idx + 1}</td>
                    <td>{player.name || player[Object.keys(player)[0]]}</td>
                    <td>{typeof player.rating === 'number' ? player.rating.toFixed(2) : (player.rating && !isNaN(Number(player.rating)) ? Number(player.rating).toFixed(2) : 'N/A')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    </div>
  );
}
