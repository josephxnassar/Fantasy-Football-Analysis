import { formatStatForDisplay, getStatDefinition, getStatLabel } from '../../utils/statDefinitions';
import { getStatColorClass } from '../../utils/statColorHelpers';

export default function AggregateStatsGrid({ groupedStats }) {
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
