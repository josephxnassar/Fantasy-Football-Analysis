import AggregateStatsGrid from './AggregateStatsGrid';
import WeeklyStatsRows from './WeeklyStatsRows';

function hasStats(groupedStats) {
  return Object.values(groupedStats || {}).some((stats) => Object.keys(stats).length > 0);
}

export default function PlayerStatsTabLayout({
  title,
  playerDetails,
  currentSeason,
  viewMode,
  groupSeasonRecord,
  groupWeeklyRecord = groupSeasonRecord,
  emptySeasonText = 'No seasonal data available',
  emptyWeeklyText = 'No weekly data available',
}) {
  const groupedSeasonStats = groupSeasonRecord(playerDetails?.stats || {}, playerDetails?.position);

  return (
    <div className="stats-section">
      <h3>{title} {currentSeason ? `(${currentSeason} Season)` : '(Most Recent Season)'}</h3>
      {viewMode === 'aggregate' ? (
        hasStats(groupedSeasonStats)
          ? <AggregateStatsGrid groupedStats={groupedSeasonStats} />
          : <p className="player-details-no-data">{emptySeasonText}</p>
      ) : (
        <WeeklyStatsRows
          playerDetails={playerDetails}
          currentSeason={currentSeason}
          groupWeeklyRecord={groupWeeklyRecord}
          emptyWeeklyText={emptyWeeklyText}
        />
      )}
    </div>
  );
}
