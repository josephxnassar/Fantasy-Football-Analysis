import AggregateStatsGrid from './AggregateStatsGrid';
import WeeklyStatsRows from './WeeklyStatsRows';

function hasStats(groupedStats) {
  return Object.values(groupedStats || {}).some((stats) => Object.keys(stats).length > 0);
}

export default function PlayerStatsTabLayout({
  title,
  statsContext,
  groupSeasonRecord,
  groupWeeklyRecord = groupSeasonRecord,
  emptySeasonText = 'No seasonal data available',
  emptyWeeklyText = 'No weekly data available',
}) {
  const { playerDetails, currentSeason, viewMode } = statsContext;
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
          statsContext={statsContext}
          groupWeeklyRecord={groupWeeklyRecord}
          emptyWeeklyText={emptyWeeklyText}
        />
      )}
    </div>
  );
}
