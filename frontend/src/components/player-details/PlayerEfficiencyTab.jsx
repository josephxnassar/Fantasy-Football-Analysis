import { groupStatsByCategoryMap } from '../../utils/statDefinitions';
import { EFFICIENCY_CATEGORY_MAP } from './statTabConfigs';
import PlayerStatsTabLayout from './PlayerStatsTabLayout';

// Applies the efficiency category map to either seasonal or weekly records.
function groupEfficiencyStats(record) {
  return groupStatsByCategoryMap(record, EFFICIENCY_CATEGORY_MAP, { hideZero: true });
}

export default function PlayerEfficiencyTab({ statsContext }) {
  return (
    <PlayerStatsTabLayout
      title="Efficiency Profile"
      statsContext={statsContext}
      groupSeasonRecord={groupEfficiencyStats}
      groupWeeklyRecord={groupEfficiencyStats}
      emptySeasonText="No efficiency data available"
      emptyWeeklyText="No efficiency weekly data available"
    />
  );
}
