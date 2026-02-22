import { groupStatsByCategoryMap } from '../../utils/statDefinitions';
import { OPPORTUNITY_CATEGORY_MAP } from './statTabConfigs';
import PlayerStatsTabLayout from './PlayerStatsTabLayout';

function groupOpportunityStats(record) {
  return groupStatsByCategoryMap(record, OPPORTUNITY_CATEGORY_MAP, { hideZero: true });
}

export default function PlayerOpportunityTab({ statsContext }) {
  return (
    <PlayerStatsTabLayout
      title="Role & Opportunity"
      statsContext={statsContext}
      groupSeasonRecord={groupOpportunityStats}
      groupWeeklyRecord={groupOpportunityStats}
      emptySeasonText="No opportunity data available"
      emptyWeeklyText="No opportunity weekly data available"
    />
  );
}
