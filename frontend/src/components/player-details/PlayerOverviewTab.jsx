import { groupStatsByCategoryMap } from '../../utils/statDefinitions';
import { PRODUCTION_GROUPS } from '../../utils/statMeta';
import PlayerStatsTabLayout from './PlayerStatsTabLayout';

function groupProductionStats(record, position) {
  const groups = PRODUCTION_GROUPS[position] || PRODUCTION_GROUPS.Overall;
  return groupStatsByCategoryMap(record, groups);
}

export default function PlayerOverviewTab({ statsContext }) {
  return (
    <PlayerStatsTabLayout
      title="Production"
      statsContext={statsContext}
      groupSeasonRecord={groupProductionStats}
      groupWeeklyRecord={groupProductionStats}
      emptySeasonText="No production data available"
      emptyWeeklyText="No weekly production data available"
    />
  );
}
