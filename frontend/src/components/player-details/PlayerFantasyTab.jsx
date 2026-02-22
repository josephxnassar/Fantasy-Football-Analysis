import { groupStatsByPosition } from '../../utils/statDefinitions';
import { adaptPlayerDetailsForDisplay } from '../../utils/playerStatsAdapter';
import PlayerStatsTabLayout from './PlayerStatsTabLayout';

function groupFantasyStats(record, position) {
  return groupStatsByPosition(record, position);
}

export default function PlayerFantasyTab({ playerDetails, currentSeason, viewMode }) {
  const displayDetails = adaptPlayerDetailsForDisplay(playerDetails);

  return (
    <PlayerStatsTabLayout
      title="Fantasy Production"
      playerDetails={displayDetails}
      currentSeason={currentSeason}
      viewMode={viewMode}
      groupSeasonRecord={groupFantasyStats}
      groupWeeklyRecord={groupFantasyStats}
      emptySeasonText="No fantasy seasonal data available"
      emptyWeeklyText="No fantasy weekly data available"
    />
  );
}
