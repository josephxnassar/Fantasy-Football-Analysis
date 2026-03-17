/**
 * File overview: Component for Team Schedule Game Card within the teams feature.
 */

import { getTeamColor } from '../../shared/utils/teamColors';

function getResultLabel(game, team) {
  if (!game?.winner) return null;
  if (game.winner === 'TIE') return 'TIE';
  return game.winner === team ? 'W' : 'L';
}

export default function TeamScheduleGameCard({ game, team, teamColor, expanded, onToggle }) {
  const isByeWeek = game.opponent === 'BYE';
  const isHomeGame = !isByeWeek && game.home_away === 'HOME';
  const opponentColor = isByeWeek ? null : getTeamColor(game.opponent);
  const resultLabel = getResultLabel(game, team);
  const gameTileStyle = isHomeGame ? { '--home-corner-color': teamColor } : undefined;
  const className = ['schedule-game', isByeWeek ? 'bye' : 'interactive', isHomeGame ? 'home-game' : '', expanded ? 'expanded' : '']
    .filter(Boolean)
    .join(' ');

  return (
    <button type="button" className={className} style={gameTileStyle} onClick={() => onToggle(game.week, isByeWeek)}>
      <span className="game-week">Week {game.week}</span>
      <span className={`game-opponent ${isByeWeek ? 'bye-text' : ''}`}>
        {isByeWeek ? (
          'BYE'
        ) : (
          <>
            <span
              className={`game-prefix ${game.home_away === 'AWAY' ? 'away' : 'home'}`}
              style={game.home_away === 'AWAY' ? { color: opponentColor } : undefined}
            >
              {game.home_away === 'AWAY' ? '@' : 'vs'}
            </span>
            <span className="game-opponent-code" style={{ color: opponentColor }}>
              {game.opponent}
            </span>
          </>
        )}
      </span>

      {!isByeWeek && resultLabel && (
        <span className={`game-result-pill ${resultLabel === 'W' ? 'win' : resultLabel === 'L' ? 'loss' : 'tie'}`}>{resultLabel}</span>
      )}

      {expanded && !isByeWeek && (
        <div className="game-details">
          {game.team_score !== null && game.opponent_score !== null ? (
            <>
              <div className="game-scoreline">
                <span className={game.winner === team ? 'winner' : ''}>
                  {team} {game.team_score}
                </span>
                <span className="game-score-separator">-</span>
                <span className={game.winner === game.opponent ? 'winner' : ''}>
                  {game.opponent} {game.opponent_score}
                </span>
              </div>
              <div className="game-winner-line">Winner: {game.winner === 'TIE' ? 'Tie' : game.winner}</div>
            </>
          ) : (
            <div className="game-winner-line">Score unavailable.</div>
          )}
        </div>
      )}
    </button>
  );
}
