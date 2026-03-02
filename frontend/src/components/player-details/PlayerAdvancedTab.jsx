import { groupStatsByCategoryMap } from '../../utils/statDefinitions';
import { ADVANCED_CATEGORY_MAP } from './statTabConfigs';
import PlayerStatsTabLayout from './PlayerStatsTabLayout';

// Advanced tab: efficiency metrics, Next Gen tracking, PFR detail (split by category).
function groupAdvancedStats(record) {
  return groupStatsByCategoryMap(record, ADVANCED_CATEGORY_MAP, { hideZero: true });
}

export default function PlayerAdvancedTab({ statsContext }) {
  return (
    <PlayerStatsTabLayout
      title="Advanced Metrics"
      statsContext={statsContext}
      groupSeasonRecord={groupAdvancedStats}
      groupWeeklyRecord={groupAdvancedStats}
      emptySeasonText="No advanced data available"
      emptyWeeklyText="No advanced weekly data available"
    />
  );
}
