import { useCallback, useRef, useState } from 'react';
import { getTeamSchedule } from '../../api';
import { useTeamModalData } from '../../shared/hooks/useTeamModalData';
import { getTeamColor } from '../../shared/utils/teamColors';
import { ModalBackdrop } from '../../shared/ui';
import './TeamScheduleModal.css';

export default function TeamScheduleModal({ team, onClose }) {
  const [selectedSeason, setSelectedSeason] = useState(null);
  const [expandedWeek, setExpandedWeek] = useState(null);
  const prevTeamRef = useRef(team);

  const fetchSchedule = useCallback((t) => {
    if (t !== prevTeamRef.current) {
      prevTeamRef.current = t;
      setSelectedSeason(null);
      setExpandedWeek(null);
      return getTeamSchedule(t, null);
    }
    return getTeamSchedule(t, selectedSeason);
  }, [selectedSeason]);

  const { data: schedule, loading, error } = useTeamModalData(team, fetchSchedule, 'Failed to load schedule');
  const scheduleTeamColor = getTeamColor(schedule?.team || team);
  const teamHeaderColor = { color: scheduleTeamColor };

  const handleSeasonChange = (event) => {
    setSelectedSeason(Number(event.target.value));
    setExpandedWeek(null);
  };

  const toggleGameDetails = (week, isBye) => {
    if (isBye)
      return;
    setExpandedWeek((previousWeek) => (previousWeek === week ? null : week));
  };

  const getResultLabel = (game) => {
    if (!game?.winner)
      return null;
    if (game.winner === 'TIE')
      return 'TIE';
    if (game.winner === schedule.team)
      return 'W';
    return 'L';
  };

  if (!team)
    return null;

  return (
    <ModalBackdrop onClose={onClose}>
      <div className="schedule-modal-content">
        <button className="schedule-close-button" onClick={onClose}>×</button>
        {loading && <div className="loading">Loading schedule...</div>}
        {error && <div className="error">{error}</div>}
        {schedule && !loading && (
          <>
            <div className="schedule-header">
              <h2 className="team-title" style={teamHeaderColor}>{schedule.team}</h2>
              <p className="team-full-name">{schedule.team_name}</p>
              {schedule.available_seasons?.length > 1 && (
                <div className="schedule-season-selector">
                  <label htmlFor="schedule-season">Season:</label>
                  <select id="schedule-season" value={selectedSeason ?? schedule.season} onChange={handleSeasonChange}>
                    {schedule.available_seasons.map((season) => (<option key={season} value={season}>{season}</option>))}
                  </select>
                </div>
              )}
              {schedule.bye_week && (<div className="bye-week-badge">Bye Week: {schedule.bye_week}</div>)}
            </div>
            <div className="schedule-grid">
              {schedule.schedule.map((game) => {
                const isGame = game.opponent !== 'BYE';
                const isHomeGame = isGame && game.home_away === 'HOME';
                const opponentColor = isGame ? getTeamColor(game.opponent) : null;
                const gameTileStyle = isHomeGame ? { '--home-corner-color': scheduleTeamColor } : undefined;

                return (
                  <button type="button" key={game.week} className={`schedule-game ${game.opponent === 'BYE' ? 'bye' : 'interactive'} ${isHomeGame ? 'home-game' : ''} ${expandedWeek === game.week ? 'expanded' : ''}`} style={gameTileStyle} onClick={() => toggleGameDetails(game.week, game.opponent === 'BYE')}>
                    <span className="game-week">Week {game.week}</span>
                    <span className={`game-opponent ${game.opponent === 'BYE' ? 'bye-text' : ''}`}>
                      {game.opponent === 'BYE' ? ('BYE') : (
                        <>
                          <span className={`game-prefix ${game.home_away === 'AWAY' ? 'away' : 'home'}`} style={game.home_away === 'AWAY' ? { color: opponentColor } : undefined}>{game.home_away === 'AWAY' ? '@' : 'vs'}</span>
                          <span className="game-opponent-code" style={{ color: opponentColor }}>{game.opponent}</span>
                        </>
                      )}
                    </span>
                    {game.opponent !== 'BYE' && getResultLabel(game) && (<span className={`game-result-pill ${getResultLabel(game) === 'W' ? 'win' : getResultLabel(game) === 'L' ? 'loss' : 'tie'}`}>{getResultLabel(game)}</span>)}

                    {expandedWeek === game.week && game.opponent !== 'BYE' && (
                      <div className="game-details">
                        {game.team_score !== null && game.opponent_score !== null ? (
                          <>
                            <div className="game-scoreline">
                              <span className={game.winner === schedule.team ? 'winner' : ''}>
                                {schedule.team} {game.team_score}
                              </span>
                              <span className="game-score-separator">-</span>
                              <span className={game.winner === game.opponent ? 'winner' : ''}>
                                {game.opponent} {game.opponent_score}
                              </span>
                            </div>
                            <div className="game-winner-line">Winner: {game.winner === 'TIE' ? 'Tie' : game.winner}</div>
                          </>
                        ) : (<div className="game-winner-line">Score unavailable.</div>)}
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </>
        )}
      </div>
    </ModalBackdrop>
  );
}
