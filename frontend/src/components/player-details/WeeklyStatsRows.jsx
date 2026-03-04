import AggregateStatsGrid from './AggregateStatsGrid';

function getWeekMatchupLabel(week) {
  // Supports both current and legacy opponent field names.
  const opponent = week?.opponent_team ?? week?.team_opponent;
  return opponent ? `vs ${opponent}` : null;
}

function hasWeeklyCategories(groupedStats) {
  return Object.values(groupedStats || {}).some((stats) => Object.keys(stats).length > 0);
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
        // Tab-specific grouper controls which weekly stats render for this tab.
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
            {hasWeeklyCategories(groupedStats) ? (
              <AggregateStatsGrid groupedStats={groupedStats} />
            ) : (
              <p className="week-no-stats">No stats recorded</p>
            )}
          </div>
        );
      })}
    </div>
  );
}
