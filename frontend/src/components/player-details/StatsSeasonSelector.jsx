import { useId } from 'react';

export default function StatsSeasonSelector({availableSeasons, currentSeason, onSeasonChange}) {
  const selectId = useId();

  if (availableSeasons.length <= 1) 
    return null;

  return (
    <div className="year-selector">
      <label className="year-label" htmlFor={selectId}>Season</label>
      <select id={selectId} className="year-select" value={currentSeason != null ? String(currentSeason) : ''} onChange={(event) => {const nextSeason = Number(event.target.value); onSeasonChange(Number.isNaN(nextSeason) ? event.target.value : nextSeason);}}>
        {availableSeasons.map((season) => (<option key={season} value={season}>{season}</option>))}
      </select>
    </div>
  );
}
