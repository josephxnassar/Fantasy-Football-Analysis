import { groupStatsByCategoryMap } from '../../utils/statDefinitions';
import { USAGE_CATEGORY_MAP } from './statTabConfigs';
import PlayerStatsTabLayout from './PlayerStatsTabLayout';

// Usage tab covers share signals, opportunity model, realized outcomes, and delta.
function groupUsageStats(record) {
  return groupStatsByCategoryMap(record, USAGE_CATEGORY_MAP, { hideZero: true });
}

export default function PlayerUsageTab({ statsContext }) {
  return (
    <PlayerStatsTabLayout
      title="Usage & Opportunity"
      statsContext={statsContext}
      groupSeasonRecord={groupUsageStats}
      groupWeeklyRecord={groupUsageStats}
      emptySeasonText="No usage data available"
      emptyWeeklyText="No usage weekly data available"
    />
  );
}
