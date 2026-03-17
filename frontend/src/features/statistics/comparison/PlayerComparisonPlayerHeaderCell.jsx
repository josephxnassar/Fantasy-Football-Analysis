/**
 * File overview: Component for Player Comparison Player Header Cell within the player comparison feature.
 */

export default function PlayerComparisonPlayerHeaderCell({ slot, wins, onPlayerHeaderClick }) {
  return (
    <th>
      <div className="direct-comparison-column-header">
        <button type="button" className="direct-comparison-player-link" title={slot.playerName} onClick={() => onPlayerHeaderClick(slot)}>
          {slot.playerName}
        </button>
        <small>{slot.season ?? 'Latest'}</small>
        <small className="direct-comparison-wins-label">Wins: {wins}</small>
      </div>
    </th>
  );
}
