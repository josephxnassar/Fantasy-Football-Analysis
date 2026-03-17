/**
 * File overview: Component for Player Comparison Weeks Row within the player comparison feature.
 */

import { StatTooltip } from '../../../shared/ui';
import PlayerComparisonValueCell from './PlayerComparisonValueCell';

export default function PlayerComparisonWeeksRow({ selectedPlayers, weeksWinners }) {
  return (
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
        return <PlayerComparisonValueCell key={`${slot.id}-weeks-played`} displayValue={displayValue} isWinner={isWinner} />;
      })}
    </tr>
  );
}
