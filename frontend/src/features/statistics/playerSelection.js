/**
 * File overview: Shared helper for opening either a season-specific player view or the generic player modal from statistics surfaces.
 */

export function openPlayerSelection({ playerName, season, onPlayerClick, onPlayerSeasonClick }) {
  if (!playerName) return;

  const hasSeason = season !== null && season !== undefined && season !== '';
  const selectedSeason = hasSeason ? Number(season) : Number.NaN;
  if (onPlayerSeasonClick && Number.isFinite(selectedSeason)) {
    onPlayerSeasonClick(playerName, selectedSeason);
    return;
  }

  onPlayerClick?.(playerName);
}
