/**
 * File overview: Component for Player Overview Tab within the player details feature.
 */

import { groupStatsByCategoryMap } from '../../../shared/utils/statDefinitions';
import { getProductionGroups } from '../../../shared/utils/statMeta';
import SeasonalStatsRow from './SeasonalStatsRow';
import WeeklyStatsRows from './WeeklyStatsRows';

function groupProductionStats(record, position) {
  return groupStatsByCategoryMap(record, getProductionGroups(position));
}

export default function PlayerOverviewTab({ statsContext }) {
  const { playerDetails, currentSeason, viewMode } = statsContext;
  const groupedSeasonStats = groupProductionStats(playerDetails?.stats || {}, playerDetails?.position);

  return (
    <div className="stats-section">
      <h3>Production {currentSeason ? `(${currentSeason} Season)` : '(Most Recent Season)'}</h3>
      {viewMode === 'aggregate' ? (
        <SeasonalStatsRow groupedStats={groupedSeasonStats} />
      ) : (
        <WeeklyStatsRows
          statsContext={statsContext}
          groupWeeklyRecord={groupProductionStats}
          emptyWeeklyText="No weekly production data available"
        />
      )}
    </div>
  );
}
