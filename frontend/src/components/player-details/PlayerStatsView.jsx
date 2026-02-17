import { getStatDefinition, groupStatsByPosition } from '../../utils/statDefinitions';
import { formatStatValue } from '../../utils/helpers';
import { getStatColorClass } from '../../utils/statColorHelpers';

function formatDisplayStat(key, value) {
  if (key === 'Snap Share' && typeof value === 'number') {
    const pct = value <= 1 ? value * 100 : value;
    return `${pct.toFixed(1)}%`;
  }
  return formatStatValue(value);
}

function getWeekMatchupLabel(week) {
  const opponent = week?.opponent_team ?? week?.team_opponent;
  if (!opponent) return null;
  return `vs ${opponent}`;
}

function renderStatCategories(details) {
  const groupedStats = groupStatsByPosition(details.stats, details.position);

  return Object.entries(groupedStats).map(([category, stats]) => {
    if (Object.keys(stats).length === 0) return null;

    return (
      <div key={category} className="stat-category">
        <h4 className="category-title">{category}</h4>
        <div className="stats-grid">
          {Object.entries(stats).map(([key, value]) => (
            <div
              key={key}
              className="stat-item"
              title={getStatDefinition(key)}
            >
              <span className="stat-label">{key}</span>
              <span className="stat-value">{formatDisplayStat(key, value)}</span>
            </div>
          ))}
        </div>
      </div>
    );
  });
}

function renderWeeklyStats(playerDetails, currentSeason) {
  const weeklyStats = playerDetails?.weekly_stats;
  if (!weeklyStats || weeklyStats.length === 0) {
    return <p className="no-data">No weekly data available</p>;
  }

  const seasonWeeks = weeklyStats.filter((week) => week.season === currentSeason);
  if (seasonWeeks.length === 0) {
    return <p className="no-data">No weekly data available for {currentSeason}</p>;
  }

  seasonWeeks.sort((a, b) => (a.week || 0) - (b.week || 0));

  return (
    <div className="weekly-stats-container">
      {seasonWeeks.map((week, idx) => {
        const groupedStats = groupStatsByPosition(week, playerDetails.position);
        const matchupLabel = getWeekMatchupLabel(week);
        const coreStats = groupedStats.Core || {};
        const coreEntries = Object.entries(coreStats);
        const usageStats = groupedStats.Usage || {};
        const usageEntries = Object.entries(usageStats);
        const hasNonCoreStats = Object.entries(groupedStats).some(
          ([category, stats]) => category !== 'Core' && category !== 'Usage' && Object.keys(stats).length > 0
        );

        return (
          <div key={idx} className="weekly-breakdown">
            <div className="week-header-row">
              <h4 className="week-header">Week {week.week}</h4>
              {matchupLabel && <span className="week-matchup-badge">{matchupLabel}</span>}
            </div>
            {coreEntries.length > 0 && (
              <div className="week-ppr-row">
                {coreEntries.map(([key, value]) => (
                  <span key={key} className="week-ppr">{key}: {formatDisplayStat(key, value)}</span>
                ))}
              </div>
            )}
            {usageEntries.length > 0 && (
              <div className="week-categories">
                <div className="stat-category-group">
                  <div className="category-name">Usage</div>
                  <div className="category-stats">
                    {usageEntries.map(([key, value]) => {
                      const colorClass = getStatColorClass(key, value);
                      return (
                        <span key={key} className={`week-stat-item ${colorClass}`}>
                          {key}: {formatDisplayStat(key, value)}
                        </span>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
            {hasNonCoreStats ? (
              <div className="week-categories">
                {Object.entries(groupedStats).map(([category, stats]) => {
                  if (category === 'Core' || category === 'Usage' || Object.keys(stats).length === 0) return null;

                  return (
                    <div key={category} className="stat-category-group">
                      <div className="category-name">{category}</div>
                      <div className="category-stats">
                        {Object.entries(stats).map(([key, value]) => {
                          const colorClass = getStatColorClass(key, value);
                          return (
                            <span key={key} className={`week-stat-item ${colorClass}`}>
                              {key}: {formatDisplayStat(key, value)}
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="week-no-stats">No stats recorded</p>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default function PlayerStatsView({
  playerDetails,
  availableSeasons,
  onSeasonChange,
  currentSeason,
  viewMode,
  setViewMode,
}) {
  return (
    <>
      {availableSeasons.length > 1 && (
        <div className="year-selector">
          <span className="year-label">View Stats:</span>
          <div className="year-buttons">
            {availableSeasons.map((season) => (
              <button
                key={season}
                className={`year-button ${currentSeason === season ? 'active' : ''}`}
                onClick={() => onSeasonChange(season)}
              >
                {season}
              </button>
            ))}
          </div>
        </div>
      )}

      {playerDetails?.weekly_stats && playerDetails.weekly_stats.length > 0 && (
        <div className="view-mode-toggle">
          <button
            className={`toggle-btn ${viewMode === 'aggregate' ? 'active' : ''}`}
            onClick={() => setViewMode('aggregate')}
          >
            Season Total
          </button>
          <button
            className={`toggle-btn ${viewMode === 'weekly' ? 'active' : ''}`}
            onClick={() => setViewMode('weekly')}
          >
            By Week
          </button>
        </div>
      )}

      <div className="stats-section">
        <h3>Statistics {currentSeason ? `(${currentSeason} Season)` : '(Most Recent Season)'}</h3>
        {viewMode === 'aggregate'
          ? renderStatCategories(playerDetails)
          : renderWeeklyStats(playerDetails, currentSeason)}
      </div>
    </>
  );
}
