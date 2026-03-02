import { formatStatForDisplay, getStatDefinition, getStatLabel } from '../../utils/statDefinitions';
import { getStatColorClass } from '../../utils/statColorHelpers';
import { StatTooltip } from '../common';

export default function StatRow({ statKey, value }) {
  const colorClass = getStatColorClass(statKey, value);
  const label = getStatLabel(statKey);

  return (
    <div className={`stat-row ${colorClass}`}>
      <span className="stat-label">
        {label}
        <StatTooltip label={label} description={getStatDefinition(statKey)} />
      </span>
      <span className="stat-value">{formatStatForDisplay(statKey, value)}</span>
    </div>
  );
}
