/**
 * File overview: Component for Stat Row within the player details feature.
 */

import { formatStatForDisplay, getStatDefinition, getStatLabel } from '../../../shared/utils/statDefinitions';
import { getStatColorClass } from '../../../shared/utils/statColorHelpers';
import { StatTooltip } from '../../../shared/ui';

export default function StatRow({ statKey, value }) {
  const colorClass = getStatColorClass(statKey, value);
  const label = getStatLabel(statKey);

  return (
    <div className={`stat-row ${colorClass}`}>
      <span className="stat-label">
        <span className="stat-label-text" title={label}>
          {label}
        </span>
        <StatTooltip label={label} description={getStatDefinition(statKey)} />
      </span>
      <span className="stat-value">{formatStatForDisplay(statKey, value)}</span>
    </div>
  );
}
