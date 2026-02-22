import { formatStatForDisplay, getStatDefinition, getStatLabel } from '../../utils/statDefinitions';
import { getStatColorClass } from '../../utils/statColorHelpers';

function getWeekMatchupLabel(week) {
  const opponent = week?.opponent_team ?? week?.team_opponent;
  return opponent ? `vs ${opponent}` : null;
}

function hasStats(groupedStats) {
  return Object.values(groupedStats || {}).some((stats) => Object.keys(stats).length > 0);
}

function renderCategoryGrid(groupedStats) {
  return Object.entries(groupedStats).map(([category, stats]) => {
    const entries = Object.entries(stats);
    if (!entries.length) return null;
    return (
      <div key={category} className="stat-category">
        <h4 className="category-title">{category}</h4>
        <div className="stats-grid">
          {entries.map(([key, value]) => {
            const colorClass = getStatColorClass(key, value);
            return (
              <div key={key} className={`stat-item ${colorClass}`} title={getStatDefinition(key)}>
                <span className="stat-label">{getStatLabel(key)}</span>
                <span className="stat-value">{formatStatForDisplay(key, value)}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  });
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
                <span
                  key={key}
                  className={`week-stat-item ${colorClass}`}
                  title={getStatDefinition(key)}
                >
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

function renderWeeklyRows(playerDetails, currentSeason, groupWeeklyRecord, emptyWeeklyText) {
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
        const weekKey = week.game_id ? `${week.season}-${week.week}-${week.game_id}` : `${week.season}-${week.week}-${idx}`;

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

export default function PlayerStatsTabLayout({
  title,
  playerDetails,
  currentSeason,
  viewMode,
  groupSeasonRecord,
  groupWeeklyRecord = groupSeasonRecord,
  emptySeasonText = 'No seasonal data available',
  emptyWeeklyText = 'No weekly data available',
}) {
  const groupedSeasonStats = groupSeasonRecord(playerDetails?.stats || {}, playerDetails?.position);

  return (
    <div className="stats-section">
      <h3>{title} {currentSeason ? `(${currentSeason} Season)` : '(Most Recent Season)'}</h3>
      {viewMode === 'aggregate' ? (
        hasStats(groupedSeasonStats)
          ? renderCategoryGrid(groupedSeasonStats)
          : <p className="player-details-no-data">{emptySeasonText}</p>
      ) : (
        renderWeeklyRows(playerDetails, currentSeason, groupWeeklyRecord, emptyWeeklyText)
      )}
    </div>
  );
}
