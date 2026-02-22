import { groupStatsByCategoryMap } from '../../utils/statDefinitions';
import { INTERPRETATION_CATEGORY_MAP } from './statTabConfigs';
import PlayerStatsTabLayout from './PlayerStatsTabLayout';

function groupInterpretationStats(record) {
  return groupStatsByCategoryMap(record, INTERPRETATION_CATEGORY_MAP, { hideZero: true });
}

export default function PlayerInterpretationTab({ statsContext }) {
  return (
    <PlayerStatsTabLayout
      title="Interpretation"
      statsContext={statsContext}
      groupSeasonRecord={groupInterpretationStats}
      groupWeeklyRecord={groupInterpretationStats}
      emptySeasonText="No interpreted data available"
      emptyWeeklyText="No interpreted weekly data available"
    />
  );
}
