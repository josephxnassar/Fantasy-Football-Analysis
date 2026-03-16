import { groupStatsByCategoryMap } from '../../utils/statDefinitions';
import { PRODUCTION_GROUPS } from '../../utils/statMeta';
import SeasonalStatsRow from './SeasonalStatsRow';
import WeeklyStatsRows from './WeeklyStatsRows';

function groupProductionStats(record, position) {
  const groups = PRODUCTION_GROUPS[position] || PRODUCTION_GROUPS.Overall;
  return groupStatsByCategoryMap(record, groups);
}

export default function PlayerOverviewTab({ statsContext }) {
  const { playerDetails, currentSeason, viewMode } = statsContext;
  const groupedSeasonStats = groupProductionStats(playerDetails?.stats || {}, playerDetails?.position);

  return (
    <div className="stats-section">
      <h3>Production {currentSeason ? `(${currentSeason} Season)` : '(Most Recent Season)'}</h3>
      {viewMode === 'aggregate' ? (<SeasonalStatsRow groupedStats={groupedSeasonStats} />) : (<WeeklyStatsRows statsContext={statsContext} groupWeeklyRecord={groupProductionStats} emptyWeeklyText="No weekly production data available"/>)}
    </div>
  );
}
