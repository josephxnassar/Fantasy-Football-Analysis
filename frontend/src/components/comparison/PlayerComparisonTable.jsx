/* Comparison table view for selected player-season slots. */

import { formatStatForDisplay, getStatDefinition, getStatLabel } from '../../utils/statDefinitions';
import { EmptyStateMessage, StatTooltip } from '../common';

function isMissingStatValue(value) {
  return value === null || value === undefined || (typeof value === 'number' && Number.isNaN(value));
}

function formatComparisonValue(statKey, value) {
  if (isMissingStatValue(value)) return '—';
  return formatStatForDisplay(statKey, value);
}

export default function PlayerComparisonTable({
  selectedPlayers,
  comparisonRows,
  statWinnersByKey,
  weeksWinners,
  winCountsBySlot,
  onPlayerClick,
}) {
  if (selectedPlayers.length === 0) {
    return <EmptyStateMessage message="Select at least one player to compare." />;
  }

  return (
    <div className="direct-comparison-table-wrapper">
      <table className="direct-comparison-table">
        <thead>
          <tr>
            <th>Stat</th>
            {selectedPlayers.map((slot) => (
              <th key={slot.id}>
                <div className="direct-comparison-column-header">
                  <button
                    type="button"
                    className="direct-comparison-player-link"
                    onClick={() => onPlayerClick?.(slot.playerName)}
                  >
                    {slot.playerName}
                  </button>
                  <small>{slot.season ?? 'Latest'}</small>
                  <small className="direct-comparison-wins-label">
                    Wins: {winCountsBySlot[slot.id] || 0}
                  </small>
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row" className="direct-comparison-stat-cell">
              <span className="direct-comparison-stat-label">
                <span>Weeks Played</span>
                <StatTooltip
                  label="Weeks Played"
                  description="Number of weekly game logs recorded for the selected season."
                />
              </span>
            </th>
            {selectedPlayers.map((slot) => {
              const displayValue = slot.loading ? '...' : (slot.weeksPlayed ?? '—');
              const isWinner = weeksWinners.has(slot.id) && displayValue !== '—';
              return (
                <td
                  key={`${slot.id}-weeks-played`}
                  className={[
                    displayValue === '—' ? 'direct-comparison-value-missing' : '',
                    isWinner ? 'direct-comparison-value-winner' : '',
                  ].filter(Boolean).join(' ')}
                >
                  {displayValue}
                </td>
              );
            })}
          </tr>

          {comparisonRows.map((row) => {
            if (row.type === 'category') {
              return (
                <tr key={row.id} className="direct-comparison-category-row">
                  <th colSpan={selectedPlayers.length + 1}>{row.label}</th>
                </tr>
              );
            }

            const statLabel = getStatLabel(row.statKey);
            const statDescription = getStatDefinition(row.statKey);

            return (
              <tr key={row.id}>
                <th scope="row" className="direct-comparison-stat-cell">
                  <span className="direct-comparison-stat-label">
                    <span>{statLabel}</span>
                    <StatTooltip
                      label={statLabel}
                      description={statDescription}
                    />
                  </span>
                </th>
                {selectedPlayers.map((slot) => {
                  const rawValue = slot.loading ? null : slot.stats?.[row.statKey];
                  const displayValue = slot.loading ? '...' : formatComparisonValue(row.statKey, rawValue);
                  const winners = statWinnersByKey[row.statKey] || new Set();
                  const isWinner = winners.has(slot.id) && displayValue !== '—';
                  return (
                    <td
                      key={`${slot.id}-${row.statKey}`}
                      className={[
                        displayValue === '—' ? 'direct-comparison-value-missing' : '',
                        isWinner ? 'direct-comparison-value-winner' : '',
                      ].filter(Boolean).join(' ')}
                    >
                      {displayValue}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
