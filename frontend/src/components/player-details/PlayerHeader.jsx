import { RookieBadge } from '../common';

export default function PlayerHeader({ playerDetails, rankingData }) {
  return (
    <div className="player-header">
      <div className="player-info">
        <div className="player-name-row">
          <h2>{playerDetails.name}</h2>
          <RookieBadge isRookie={rankingData?.is_rookie} size="medium" />
        </div>
        <div className="player-meta">
          {playerDetails.team && <span className="meta-item">{playerDetails.team}</span>}
          <span className="meta-item">{playerDetails.position}</span>
          {rankingData?.age && <span className="meta-item">Age {rankingData.age}</span>}
        </div>
      </div>
      <img
        src={playerDetails?.headshot_url || '/vacant-player.svg'}
        alt={playerDetails?.headshot_url ? playerDetails.name : 'No headshot available'}
        className="player-headshot"
        onError={(e) => { e.target.src = '/vacant-player.svg'; }}
      />
    </div>
  );
}
