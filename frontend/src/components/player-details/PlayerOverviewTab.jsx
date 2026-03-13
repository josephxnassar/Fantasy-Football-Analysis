import AggregateStatsGrid from './AggregateStatsGrid';
import { groupStatsByCategoryMap } from '../../utils/statDefinitions';
import { PRODUCTION_GROUPS } from '../../utils/statMeta';
import WeeklyStatsRows from './WeeklyStatsRows';

function groupProductionStats(record, position) {
  const groups = PRODUCTION_GROUPS[position] || PRODUCTION_GROUPS.Overall;
  return groupStatsByCategoryMap(record, groups);
}

function hasStats(groupedStats) {
  return Object.values(groupedStats || {}).some((stats) => Object.keys(stats).length > 0);
}

export default function PlayerOverviewTab({ statsContext }) {
  const { playerDetails, currentSeason, viewMode } = statsContext;
  const groupedSeasonStats = groupProductionStats(playerDetails?.stats || {}, playerDetails?.position);

  return (
    <div className="stats-section">
      <h3>Production {currentSeason ? `(${currentSeason} Season)` : '(Most Recent Season)'}</h3>
      {viewMode === 'aggregate' ? (
        hasStats(groupedSeasonStats) ? (
          <AggregateStatsGrid groupedStats={groupedSeasonStats} />
        ) : (
          <p className="player-details-no-data">No production data available</p>
        )
      ) : (
        <WeeklyStatsRows
          statsContext={statsContext}
          groupWeeklyRecord={groupProductionStats}
          emptyWeeklyText="No weekly production data available"
        />
      )}
    </div>
  );
}
