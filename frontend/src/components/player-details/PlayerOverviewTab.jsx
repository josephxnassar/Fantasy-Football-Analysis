import { groupStatsByPosition, groupStatsByCategoryMap } from '../../utils/statDefinitions';
import { OVERVIEW_EXTRAS_MAP } from './statTabConfigs';
import PlayerStatsTabLayout from './PlayerStatsTabLayout';

// Overview combines position-aware fantasy groups with percentile rankings.
function groupOverviewStats(record, position) {
  const positionGroups = groupStatsByPosition(record, position);
  const extras = groupStatsByCategoryMap(record, OVERVIEW_EXTRAS_MAP, { hideZero: true });
  return { ...positionGroups, ...extras };
}

export default function PlayerOverviewTab({ statsContext }) {
  return (
    <PlayerStatsTabLayout
      title="Overview"
      statsContext={statsContext}
      groupSeasonRecord={groupOverviewStats}
      groupWeeklyRecord={groupOverviewStats}
      emptySeasonText="No overview data available"
      emptyWeeklyText="No overview weekly data available"
    />
  );
}
