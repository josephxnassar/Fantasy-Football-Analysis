/**
 * File overview: Component for Selectable Player Card within the shared UI layer.
 */

import './SelectablePlayerCard.css';
import RookieBadge from './RookieBadge';
import DetailBadge from './DetailBadge';

export default function SelectablePlayerCard({ player, onPlayerClick }) {
  return (
    <button type="button" className="player-card" onClick={() => onPlayerClick(player.name, player)}>
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
    </button>
  );
}
