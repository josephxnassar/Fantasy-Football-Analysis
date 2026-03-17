export default function PlayerComparisonHeader({ comparisonProfileLabel, selectedCount, maxPlayers }) {
  return (
    <div className="direct-comparison-panel direct-comparison-panel--header">
      <div className="direct-comparison-copy">
        <p className="direct-comparison-kicker">Player Comparison</p>
        <h1>Player Comparison</h1>
        <p className="direct-comparison-subtitle">
          Pick up to {maxPlayers} players, then select each player&apos;s season. The comparison categories adapt automatically
          to the selected positions.
        </p>
      </div>

      <div className="direct-comparison-controls">
        <div className="direct-comparison-active-profile" aria-live="polite">
          <span className="direct-comparison-active-profile-label">Detected Profile</span>
          <strong>{comparisonProfileLabel}</strong>
        </div>
        <p className="direct-comparison-selection-count">
          {selectedCount} / {maxPlayers} selected
        </p>
      </div>
    </div>
  );
}
