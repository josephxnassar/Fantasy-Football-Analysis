import { formatStatForDisplay, getStatDefinition, getStatLabel } from '../../../shared/utils/statDefinitions';
import { StatTooltip } from '../../../shared/ui';
import PlayerComparisonValueCell from './PlayerComparisonValueCell';

function isMissingStatValue(value) {
  return value === null || value === undefined || (typeof value === 'number' && Number.isNaN(value));
}

function formatComparisonValue(statKey, value) {
  if (isMissingStatValue(value)) return '—';
  return formatStatForDisplay(statKey, value);
}

export default function PlayerComparisonStatRow({ row, selectedPlayers, statWinnersByKey }) {
  const statLabel = getStatLabel(row.statKey);
  const statDescription = getStatDefinition(row.statKey);
  const winners = statWinnersByKey[row.statKey] || new Set();

  return (
    <tr>
      <th scope="row" className="direct-comparison-stat-cell">
        <span className="direct-comparison-stat-label">
          <span>{statLabel}</span>
          <StatTooltip label={statLabel} description={statDescription} />
        </span>
      </th>
      {selectedPlayers.map((slot) => {
        const rawValue = slot.loading ? null : slot.stats?.[row.statKey];
        const displayValue = slot.loading ? '...' : formatComparisonValue(row.statKey, rawValue);
        const isWinner = winners.has(slot.id) && displayValue !== '—';
        return <PlayerComparisonValueCell key={`${slot.id}-${row.statKey}`} displayValue={displayValue} isWinner={isWinner} />;
      })}
    </tr>
  );
}
