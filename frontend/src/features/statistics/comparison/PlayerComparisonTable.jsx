import { EmptyStateMessage } from '../../../shared/ui';
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
