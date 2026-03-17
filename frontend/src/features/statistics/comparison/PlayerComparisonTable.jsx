// Comparison table for the selected player-season slots.

import { formatStatForDisplay, getStatDefinition, getStatLabel } from '../../../shared/utils/statDefinitions';
import { EmptyStateMessage, StatTooltip } from '../../../shared/ui';

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
  onPlayerSeasonClick,
}) {
  const handlePlayerHeaderClick = (slot) => {
    if (!slot?.playerName) return;
    const selectedSeason = Number(slot.season);
    if (onPlayerSeasonClick && Number.isFinite(selectedSeason)) {
      onPlayerSeasonClick(slot.playerName, selectedSeason);
      return;
    }
    onPlayerClick?.(slot.playerName);
  };

  if (selectedPlayers.length === 0) return <EmptyStateMessage message="Select at least one player to compare." />;

  return (
    <div className="direct-comparison-table-wrapper">
      <table className="direct-comparison-table">
        <colgroup>
          <col className="direct-comparison-col-stat" />
          {selectedPlayers.map((slot) => (
            <col key={`col-${slot.id}`} className="direct-comparison-col-player" />
          ))}
        </colgroup>
        <thead>
          <tr>
            <th>Stat</th>
            {selectedPlayers.map((slot) => (
              <th key={slot.id}>
                <div className="direct-comparison-column-header">
                  <button
                    type="button"
                    className="direct-comparison-player-link"
                    title={slot.playerName}
                    onClick={() => handlePlayerHeaderClick(slot)}
                  >
                    {slot.playerName}
                  </button>
                  <small>{slot.season ?? 'Latest'}</small>
                  <small className="direct-comparison-wins-label">Wins: {winCountsBySlot[slot.id] || 0}</small>
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
                <StatTooltip label="Weeks Played" description="Number of weekly game logs recorded for the selected season." />
              </span>
            </th>
            {selectedPlayers.map((slot) => {
              const displayValue = slot.loading ? '...' : (slot.weeksPlayed ?? '—');
              const isWinner = weeksWinners.has(slot.id) && displayValue !== '—';
              const valueClassName = [
                'direct-comparison-value-chip',
                displayValue === '—' ? 'direct-comparison-value-chip--missing' : '',
                isWinner ? 'direct-comparison-value-chip--winner' : '',
              ]
                .filter(Boolean)
                .join(' ');
              return (
                <td key={`${slot.id}-weeks-played`}>
                  <span className={valueClassName}>{displayValue}</span>
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
                    <StatTooltip label={statLabel} description={statDescription} />
                  </span>
                </th>
                {selectedPlayers.map((slot) => {
                  const rawValue = slot.loading ? null : slot.stats?.[row.statKey];
                  const displayValue = slot.loading ? '...' : formatComparisonValue(row.statKey, rawValue);
                  const winners = statWinnersByKey[row.statKey] || new Set();
                  const isWinner = winners.has(slot.id) && displayValue !== '—';
                  const valueClassName = [
                    'direct-comparison-value-chip',
                    displayValue === '—' ? 'direct-comparison-value-chip--missing' : '',
                    isWinner ? 'direct-comparison-value-chip--winner' : '',
                  ]
                    .filter(Boolean)
                    .join(' ');
                  return (
                    <td key={`${slot.id}-${row.statKey}`}>
                      <span className={valueClassName}>{displayValue}</span>
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
