/**
 * File overview: Component for Player Comparison Table within the player comparison feature.
 */

import { EmptyStateMessage } from '../../../shared/ui';
import { openPlayerSelection } from '../playerSelection';
import PlayerComparisonPlayerHeaderCell from './PlayerComparisonPlayerHeaderCell';
import PlayerComparisonStatRow from './PlayerComparisonStatRow';
import PlayerComparisonWeeksRow from './PlayerComparisonWeeksRow';

export default function PlayerComparisonTable({
  selectedPlayers,
  comparisonRows,
  statWinnersByKey,
  weeksWinners,
  winCountsBySlot,
  onPlayerClick,
  onPlayerSeasonClick,
}) {
  const handlePlayerHeaderClick = (slot) =>
    openPlayerSelection({ playerName: slot?.playerName, season: slot?.season, onPlayerClick, onPlayerSeasonClick });

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
              <PlayerComparisonPlayerHeaderCell
                key={slot.id}
                slot={slot}
                wins={winCountsBySlot[slot.id] || 0}
                onPlayerHeaderClick={handlePlayerHeaderClick}
              />
            ))}
          </tr>
        </thead>
        <tbody>
          <PlayerComparisonWeeksRow selectedPlayers={selectedPlayers} weeksWinners={weeksWinners} />

          {comparisonRows.map((row) => {
            if (row.type === 'category') {
              return (
                <tr key={row.id} className="direct-comparison-category-row">
                  <th colSpan={selectedPlayers.length + 1}>{row.label}</th>
                </tr>
              );
            }

            return <PlayerComparisonStatRow key={row.id} row={row} selectedPlayers={selectedPlayers} statWinnersByKey={statWinnersByKey} />;
          })}
        </tbody>
      </table>
    </div>
  );
}
