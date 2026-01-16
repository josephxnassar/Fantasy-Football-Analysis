import React, { useState, useEffect } from 'react';
import { getRankings } from '../api';
import './Rankings.css';

export default function Rankings() {
  const [rankings, setRankings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [format, setFormat] = useState('redraft');
  const [position, setPosition] = useState(null);

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

  if (loading) return <div className="loading">Loading rankings...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!rankings) return <div className="error">No data available</div>;

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
                  <th>Tier</th>
                  <th>Percentile</th>
                </tr>
              </thead>
              <tbody>
                {players.map((player, idx) => (
                  <tr key={idx}>
                    <td>{idx + 1}</td>
                    <td>{player.name || player[Object.keys(player)[0]]}</td>
                    <td><strong>{player.tier || 'N/A'}</strong></td>
                    <td>{typeof player.percentile === 'number' ? `${player.percentile.toFixed(1)}%` : 'N/A'}</td>
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
