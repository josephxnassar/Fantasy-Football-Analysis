import { formatStatForDisplay, getStatDefinition, getStatLabel } from '../../utils/statDefinitions';
import { getStatColorClass } from '../../utils/statColorHelpers';

function getWeekMatchupLabel(week) {
  const opponent = week?.opponent_team ?? week?.team_opponent;
  return opponent ? `vs ${opponent}` : null;
}

function renderWeeklyCategories(groupedStats) {
  const categories = Object.entries(groupedStats).filter(([, stats]) => Object.keys(stats).length > 0);
  if (!categories.length) {
    return <p className="week-no-stats">No stats recorded</p>;
  }

  return (
    <div className="week-categories">
      {categories.map(([category, stats]) => (
        <div key={category} className="stat-category-group">
          <div className="category-name">{category}</div>
          <div className="category-stats">
            {Object.entries(stats).map(([key, value]) => {
              const colorClass = getStatColorClass(key, value);
              return (
                <span key={key} className={`week-stat-item ${colorClass}`} title={getStatDefinition(key)}>
                  <span className="week-stat-label">{getStatLabel(key)}</span>
                  <span className="week-stat-value">{formatStatForDisplay(key, value)}</span>
                </span>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function WeeklyStatsRows({
  statsContext,
  groupWeeklyRecord,
  emptyWeeklyText,
}) {
  const { playerDetails, currentSeason } = statsContext;
  if (!playerDetails?.position) {
    return <p className="player-details-no-data">{emptyWeeklyText}</p>;
  }

  const weeklyStats = playerDetails?.weekly_stats;
  if (!Array.isArray(weeklyStats) || !weeklyStats.length) {
    return <p className="player-details-no-data">{emptyWeeklyText}</p>;
  }

  const seasonWeeks = weeklyStats
    .filter((week) => week.season === currentSeason)
    .sort((a, b) => (a.week || 0) - (b.week || 0));
  if (!seasonWeeks.length) {
    return <p className="player-details-no-data">No weekly data available for {currentSeason}</p>;
  }

  return (
    <div className="weekly-stats-container">
      {seasonWeeks.map((week, idx) => {
        const groupedStats = groupWeeklyRecord(week, playerDetails.position);
        const matchupLabel = getWeekMatchupLabel(week);
        const weekKey = week.game_id
          ? `${week.season}-${week.week}-${week.game_id}`
          : `${week.season}-${week.week}-${idx}`;

        return (
          <div key={weekKey} className="weekly-breakdown">
            <div className="week-header-row">
              <h4 className="week-header">Week {week.week}</h4>
              {matchupLabel && <span className="week-matchup-badge">{matchupLabel}</span>}
            </div>
            {renderWeeklyCategories(groupedStats)}
          </div>
        );
      })}
    </div>
  );
}
