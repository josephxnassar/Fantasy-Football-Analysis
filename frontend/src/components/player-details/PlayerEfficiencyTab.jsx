import { groupStatsByCategoryMap } from '../../utils/statDefinitions';
import { EFFICIENCY_CATEGORY_MAP } from './statTabConfigs';
import PlayerStatsTabLayout from './PlayerStatsTabLayout';

function groupEfficiencyStats(record) {
  return groupStatsByCategoryMap(record, EFFICIENCY_CATEGORY_MAP, { hideZero: true });
}

export default function PlayerEfficiencyTab({ playerDetails, currentSeason, viewMode }) {
  return (
    <PlayerStatsTabLayout
      title="Efficiency Profile"
      playerDetails={playerDetails}
      currentSeason={currentSeason}
      viewMode={viewMode}
      groupSeasonRecord={groupEfficiencyStats}
      groupWeeklyRecord={groupEfficiencyStats}
      emptySeasonText="No efficiency data available"
      emptyWeeklyText="No efficiency weekly data available"
    />
  );
}
