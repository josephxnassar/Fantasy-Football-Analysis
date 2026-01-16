import React, { useState } from 'react';
import { getStreamingRecommendations } from '../api';
import './StreamingRecs.css';

export default function StreamingRecs() {
  const [position, setPosition] = useState('WR');
  const [week, setWeek] = useState(1);
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getStreamingRecommendations(position, week);
      setRecommendation(response.data);
    } catch (err) {
      setError(`Failed to fetch recommendations: ${err.message}`);
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePositionChange = (e) => {
    setPosition(e.target.value);
  };

  const handleWeekChange = (e) => {
    setWeek(parseInt(e.target.value));
  };

  React.useEffect(() => {
    fetchRecommendations();
  }, [position, week]);

  return (
    <div className="streaming-recs-container">
      <h2>Weekly Streaming Recommendations</h2>
      
      <div className="controls">
        <div className="control-group">
          <label>Position:</label>
          <select value={position} onChange={handlePositionChange}>
            <option value="QB">QB</option>
            <option value="RB">RB</option>
            <option value="WR">WR</option>
            <option value="TE">TE</option>
          </select>
        </div>

        <div className="control-group">
          <label>Week:</label>
          <select value={week} onChange={handleWeekChange}>
            {[...Array(17)].map((_, i) => (
              <option key={i + 1} value={i + 1}>
                Week {i + 1}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading recommendations...</div>
      ) : recommendation ? (
        <div className="recommendation-card">
          <div className="rec-header">
            <h3>{recommendation.position} Streaming for Week {recommendation.week}</h3>
          </div>

          <div className="rec-main">
            <p className="rec-text">{recommendation.recommendation}</p>
          </div>

          <div className="matchup-breakdown">
            <div className="matchup-column elite">
              <h4>Elite Matchups</h4>
              <div className="opponent-list">
                {recommendation.elite_opponents.length > 0 ? (
                  recommendation.elite_opponents.map((opp, idx) => (
                    <span key={idx} className="opponent-tag elite">
                      {opp}
                    </span>
                  ))
                ) : (
                  <p className="no-matchups">None</p>
                )}
              </div>
            </div>

            <div className="matchup-column bad">
              <h4>Avoid</h4>
              <div className="opponent-list">
                {recommendation.bad_opponents.length > 0 ? (
                  recommendation.bad_opponents.map((opp, idx) => (
                    <span key={idx} className="opponent-tag bad">
                      {opp}
                    </span>
                  ))
                ) : (
                  <p className="no-matchups">None</p>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
