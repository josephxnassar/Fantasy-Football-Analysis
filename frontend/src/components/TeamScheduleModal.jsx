import { useCallback, useRef, useState } from 'react';
import { getTeamSchedule } from '../api';
import { useTeamModalData } from '../hooks/useTeamModalData';
import { ModalOverlay } from './common';
import './TeamScheduleModal.css';

export default function TeamScheduleModal({ team, onClose }) {
  const [selectedSeason, setSelectedSeason] = useState(null);
  const prevTeamRef = useRef(team);

  const fetchSchedule = useCallback(
    (t) => {
      // Reset season when team changes to avoid stale season on new team.
      if (t !== prevTeamRef.current) {
        prevTeamRef.current = t;
        setSelectedSeason(null);
        return getTeamSchedule(t, null);
      }
      return getTeamSchedule(t, selectedSeason);
    },
    [selectedSeason]
  );

  const { data: schedule, loading, error } = useTeamModalData(team, fetchSchedule, 'Failed to load schedule');

  if (!team) return null;

  return (
    <ModalOverlay className="schedule-modal-overlay" onClose={onClose}>
      <div className="schedule-modal-content">
        <button className="schedule-close-button" onClick={onClose}>×</button>
        
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
    </ModalOverlay>
  );
}
