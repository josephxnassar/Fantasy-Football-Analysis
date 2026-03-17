import StatsCategoryGrid from './StatsCategoryGrid';

function hasSeasonCategories(groupedStats) {
  return Object.values(groupedStats || {}).some((stats) => Object.keys(stats).length > 0);
}

export default function SeasonalStatsRow({ groupedStats, emptyText = 'No production data available' }) {
  if (!hasSeasonCategories(groupedStats))
    return <p className="player-details-no-data">{emptyText}</p>;

  return <StatsCategoryGrid groupedStats={groupedStats} />;
}
