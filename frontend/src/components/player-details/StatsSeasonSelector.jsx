export default function StatsSeasonSelector({
  availableSeasons,
  currentSeason,
  onSeasonChange,
}) {
  if (availableSeasons.length <= 1) return null;

  return (
    <div className="year-selector">
      <span className="year-label">View Stats:</span>
      <div className="year-buttons">
        {availableSeasons.map((season) => (
          <button
            key={season}
            className={`year-button ${currentSeason === season ? 'active' : ''}`}
            onClick={() => onSeasonChange(season)}
          >
            {season}
          </button>
        ))}
      </div>
    </div>
  );
}
