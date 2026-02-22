import { RookieBadge } from '../common';

export default function PlayerHeader({ playerDetails }) {
  // Header stays lightweight: identity row + badge + basic metadata + headshot.
  return (
    <div className="player-header">
      <div className="player-info">
        <div className="player-name-row">
          <h2>{playerDetails.name}</h2>
          <RookieBadge isRookie={playerDetails?.is_rookie} size="medium" />
        </div>
        <div className="player-meta">
          {playerDetails.team && <span className="meta-item">{playerDetails.team}</span>}
          <span className="meta-item">{playerDetails.position}</span>
          {playerDetails?.age && <span className="meta-item">Age {playerDetails.age}</span>}
        </div>
      </div>
      <img
        src={playerDetails?.headshot_url || '/vacant-player.svg'}
        alt={playerDetails?.headshot_url ? playerDetails.name : 'No headshot available'}
        className="player-headshot"
        // Fallback keeps broken image URLs from collapsing the layout.
        onError={(e) => { e.target.src = '/vacant-player.svg'; }}
      />
    </div>
  );
}
