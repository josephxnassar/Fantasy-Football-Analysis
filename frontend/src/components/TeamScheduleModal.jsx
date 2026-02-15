import { useEffect, useState } from 'react';
import { getTeamSchedule } from '../api';
import './TeamScheduleModal.css';

export default function TeamScheduleModal({ team, onClose }) {
  const [schedule, setSchedule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSeason, setSelectedSeason] = useState(null);

  useEffect(() => {
    const fetchSchedule = async () => {
      if (!team) return;

      try {
        setLoading(true);
        const response = await getTeamSchedule(team, selectedSeason);
        setSchedule(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to load schedule');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchSchedule();
  }, [team, selectedSeason]);

  useEffect(() => {
    setSelectedSeason(null);
  }, [team]);

  if (!team) return null;

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="schedule-modal-content">
        <button className="close-button" onClick={onClose}>×</button>
        
        {loading && <div className="loading">Loading schedule...</div>}
        
        {error && <div className="error">{error}</div>}
        
        {schedule && !loading && (
          <>
            <div className="schedule-header">
              <h2 className="team-title">{schedule.team}</h2>
              <p className="team-full-name">{schedule.team_name}</p>
              {schedule.available_seasons?.length > 1 && (
                <div className="schedule-season-selector">
                  <label htmlFor="schedule-season">Season:</label>
                  <select
                    id="schedule-season"
                    value={selectedSeason ?? schedule.season}
                    onChange={(e) => setSelectedSeason(Number(e.target.value))}
                  >
                    {schedule.available_seasons.map((season) => (
                      <option key={season} value={season}>{season}</option>
                    ))}
                  </select>
                </div>
              )}
              {schedule.bye_week && (
                <div className="bye-week-badge">
                  Bye Week: {schedule.bye_week}
                </div>
              )}
            </div>
            
            <div className="schedule-grid">
              {schedule.schedule.map((game) => (
                <div 
                  key={game.week} 
                  className={`schedule-game ${game.opponent === 'BYE' ? 'bye' : ''}`}
                >
                  <span className="game-week">Week {game.week}</span>
                  <span className={`game-opponent ${game.opponent === 'BYE' ? 'bye-text' : ''} ${game.home_away === 'AWAY' ? 'away' : game.home_away === 'HOME' ? 'home' : ''}`}>
                    {game.opponent === 'BYE' ? 'BYE' : `${game.home_away === 'AWAY' ? '@' : 'vs'} ${game.opponent}`}
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
