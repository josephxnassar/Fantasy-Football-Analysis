export default function StatsViewModeToggle({ viewMode, setViewMode, hasWeeklyData }) {
  // Weekly toggle appears only when week-level rows exist for the active season.
  if (!hasWeeklyData) return null;

  return (
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
  );
}
