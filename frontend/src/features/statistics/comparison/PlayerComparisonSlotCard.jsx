/**
 * File overview: Component for Player Comparison Slot Card within the player comparison feature.
 */

export default function PlayerComparisonSlotCard({
  slot,
  playerOptions,
  playerOptionsError,
  onPlayerSelect,
  onSeasonChange,
  onRemovePlayer,
}) {
  return (
    <article className="direct-comparison-slot-card">
      <div className="direct-comparison-slot-header">
        <h3>Slot {slot.id}</h3>
        {slot.playerName && (
          <button type="button" className="direct-comparison-slot-remove" onClick={() => onRemovePlayer(slot.id)}>
            Remove
          </button>
        )}
      </div>

      <div className="direct-comparison-slot-field">
        <label htmlFor={`comparison-player-${slot.id}`}>Player</label>
        <select
          id={`comparison-player-${slot.id}`}
          value={slot.playerName}
          onChange={(event) => onPlayerSelect(slot.id, event.target.value)}
          disabled={Boolean(playerOptionsError) || playerOptions.length === 0}
        >
          <option value="">Select player</option>
          {playerOptions.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>

      <div className="direct-comparison-slot-field">
        <label htmlFor={`comparison-season-${slot.id}`}>Season</label>
        <select
          id={`comparison-season-${slot.id}`}
          value={slot.season ?? ''}
          onChange={(event) => onSeasonChange(slot.id, event.target.value)}
          disabled={!slot.playerName || slot.loading || slot.availableSeasons.length === 0}
        >
          {!slot.playerName ? (
            <option value="">Select player first</option>
          ) : (
            slot.availableSeasons.map((seasonOption) => (
              <option key={seasonOption} value={seasonOption}>
                {seasonOption}
              </option>
            ))
          )}
        </select>
      </div>

      <p className="direct-comparison-slot-meta">{slot.playerName ? [slot.position, slot.team].filter(Boolean).join(' • ') : 'No player selected'}</p>
      {slot.loading && <p className="direct-comparison-player-status">Loading player data...</p>}
      {slot.error && <p className="direct-comparison-player-error">{slot.error}</p>}
    </article>
  );
}
