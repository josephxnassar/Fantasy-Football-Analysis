/**
 * File overview: Component for Player Comparison Slots Panel within the player comparison feature.
 */

import { ErrorMessage, LoadingMessage } from '../../../shared/ui';
import PlayerComparisonSlotCard from './PlayerComparisonSlotCard';

export default function PlayerComparisonSlotsPanel({
  comparisonSlots,
  playerOptionsLoading,
  playerOptionsError,
  selectionError,
  playerOptions,
  onPlayerSelect,
  onSeasonChange,
  onRemovePlayer,
}) {
  return (
    <div className="direct-comparison-panel direct-comparison-panel--selectors">
      <h2>Player Slots</h2>
      {playerOptionsLoading ? (
        <LoadingMessage message="Loading player options..." />
      ) : (
        <>
          {playerOptionsError && <ErrorMessage message={playerOptionsError} />}
          {selectionError && <ErrorMessage message={selectionError} />}

          <div className="direct-comparison-slot-grid">
            {comparisonSlots.map((slot) => (
              <PlayerComparisonSlotCard
                key={slot.id}
                slot={slot}
                playerOptions={playerOptions}
                playerOptionsError={playerOptionsError}
                onPlayerSelect={onPlayerSelect}
                onSeasonChange={onSeasonChange}
                onRemovePlayer={onRemovePlayer}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
