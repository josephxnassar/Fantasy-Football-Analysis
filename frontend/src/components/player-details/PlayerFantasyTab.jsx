import { groupStatsByPosition } from '../../utils/statDefinitions';
import PlayerStatsTabLayout from './PlayerStatsTabLayout';

function groupFantasyStats(record, position) {
  return groupStatsByPosition(record, position);
}

export default function PlayerFantasyTab({ playerDetails, currentSeason, viewMode }) {
  return (
    <PlayerStatsTabLayout
      title="Fantasy Production"
      playerDetails={playerDetails}
      currentSeason={currentSeason}
      viewMode={viewMode}
      groupSeasonRecord={groupFantasyStats}
      groupWeeklyRecord={groupFantasyStats}
      emptySeasonText="No fantasy seasonal data available"
      emptyWeeklyText="No fantasy weekly data available"
    />
  );
}
