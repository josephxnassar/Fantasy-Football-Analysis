import { formatStatForDisplay, getStatDefinition, getStatLabel } from '../../utils/statDefinitions';
import { getStatColorClass } from '../../utils/statColorHelpers';
import { StatTooltip } from '../common';

export default function AggregateStatsGrid({ groupedStats }) {
  return Object.entries(groupedStats).map(([category, stats]) => {
    const entries = Object.entries(stats);
    if (!entries.length) return null;

    return (
      <div key={category} className="stat-category">
        <h4 className="category-title">{category}</h4>
        <div className="stats-table">
          {entries.map(([key, value]) => {
            const colorClass = getStatColorClass(key, value);
            const label = getStatLabel(key);
            return (
              <div key={key} className={`stat-row ${colorClass}`}>
                <span className="stat-label">
                  {label}
                  <StatTooltip label={label} description={getStatDefinition(key)} />
                </span>
                <span className="stat-value">{formatStatForDisplay(key, value)}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  });
}
