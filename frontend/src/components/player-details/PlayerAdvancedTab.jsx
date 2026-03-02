import { groupStatsByCategoryMap } from '../../utils/statDefinitions';
import { ADVANCED_GROUPS } from '../../utils/statMeta';
import PlayerStatsTabLayout from './PlayerStatsTabLayout';

function groupAdvancedStats(record, position) {
  const groups = ADVANCED_GROUPS[position] || ADVANCED_GROUPS.Overall;
  return groupStatsByCategoryMap(record, groups, { hideZero: true });
}

export default function PlayerAdvancedTab({ statsContext }) {
  return (
    <PlayerStatsTabLayout
      title="Advanced"
      statsContext={statsContext}
      groupSeasonRecord={groupAdvancedStats}
      groupWeeklyRecord={groupAdvancedStats}
      emptySeasonText="No advanced data available"
      emptyWeeklyText="No advanced weekly data available"
    />
  );
}
