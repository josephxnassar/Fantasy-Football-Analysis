import StatRow from './StatRow';

export default function AggregateStatsGrid({ groupedStats }) {
  return Object.entries(groupedStats).map(([category, stats]) => {
    const entries = Object.entries(stats);
    if (!entries.length) return null;

    return (
      <div key={category} className="stat-category">
        <h4 className="category-title">{category}</h4>
        <div className="stats-table">
          {entries.map(([key, value]) => (
            <StatRow key={key} statKey={key} value={value} />
          ))}
        </div>
      </div>
    );
  });
}
