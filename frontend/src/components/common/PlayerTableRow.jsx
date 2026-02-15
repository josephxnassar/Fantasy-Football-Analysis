/* Reusable player table row component for rankings tables */

import RookieBadge from './RookieBadge';

export default function PlayerTableRow({ 
  player, 
  index, 
  ratingValue, 
  showPosition = false, 
  onPlayerClick 
}) {
  const playerName = player.playerName || player.name;
  
  return (
    <tr>
      <td>{index + 1}</td>
      <td>
        <div className="player-name-cell">
          <span 
            className="player-name-link" 
            onClick={() => onPlayerClick(playerName, player)}
          >
            {playerName}
          </span>
          <RookieBadge isRookie={player.is_rookie} size="small" />
        </div>
      </td>
      {showPosition && <td>{player.position}</td>}
      <td>{player.Age || 'N/A'}</td>
      <td>{ratingValue}</td>
    </tr>
  );
}
