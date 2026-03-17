export default function TeamScheduleHeader({ schedule, selectedSeason, onSeasonChange, teamHeaderColor }) {
  return (
    <div className="schedule-header">
      <h2 className="team-title" style={teamHeaderColor}>
        {schedule.team}
      </h2>
      <p className="team-full-name">{schedule.team_name}</p>
      {schedule.available_seasons?.length > 1 && (
        <div className="schedule-season-selector">
          <label htmlFor="schedule-season">Season:</label>
          <select id="schedule-season" value={selectedSeason ?? schedule.season} onChange={onSeasonChange}>
            {schedule.available_seasons.map((season) => (
              <option key={season} value={season}>
                {season}
              </option>
            ))}
          </select>
        </div>
      )}
      {schedule.bye_week && <div className="bye-week-badge">Bye Week: {schedule.bye_week}</div>}
    </div>
  );
}
