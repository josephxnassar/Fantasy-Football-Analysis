/* Reusable player card component for search results */

import RookieBadge from './RookieBadge';
import DetailBadge from './DetailBadge';

export default function PlayerCard({ player, onPlayerClick }) {
  return (
    <div
      className="player-card"
      onClick={() => onPlayerClick(player.name, player)}
    >
      <div className="player-card-left">
        <div className="player-name-search">
          <span>{player.name}</span>
          <RookieBadge isRookie={player.is_rookie} size="small" />
        </div>
        <div className="player-details-row">
          {player.team && <DetailBadge>{player.team}</DetailBadge>}
          <DetailBadge>{player.position}</DetailBadge>
          {player.age && <DetailBadge>Age {player.age}</DetailBadge>}
        </div>
      </div>
    </div>
  );
}
