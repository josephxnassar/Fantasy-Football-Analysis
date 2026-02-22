import { groupStatsByPosition } from '../../utils/statDefinitions';
import PlayerStatsTabLayout from './PlayerStatsTabLayout';

function groupFantasyStats(record, position) {
  return groupStatsByPosition(record, position);
}

export default function PlayerFantasyTab({ statsContext }) {
  return (
    <PlayerStatsTabLayout
      title="Fantasy Production"
      statsContext={statsContext}
      groupSeasonRecord={groupFantasyStats}
      groupWeeklyRecord={groupFantasyStats}
      emptySeasonText="No fantasy seasonal data available"
      emptyWeeklyText="No fantasy weekly data available"
    />
  );
}
