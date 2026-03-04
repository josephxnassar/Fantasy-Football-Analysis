import StatRow from './StatRow';

export default function AggregateStatsGrid({ groupedStats }) {
  const categories = Object.entries(groupedStats)
    .map(([category, stats]) => ({
      category,
      entries: Object.entries(stats),
    }))
    .filter(({ entries }) => entries.length > 0);

  return (
    <div
      className="aggregate-stats-grid"
      style={{ '--stat-category-count': categories.length }}
    >
      {categories.map(({ category, entries }) => (
        <div key={category} className="stat-category">
          <h4 className="category-title">{category}</h4>
          <div className="stats-table">
            {entries.map(([key, value]) => (
              <StatRow key={key} statKey={key} value={value} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
