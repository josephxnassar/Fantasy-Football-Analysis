import PlayerComparisonHeader from './PlayerComparisonHeader';
import PlayerComparisonSlotsPanel from './PlayerComparisonSlotsPanel';
import PlayerComparisonTable from './PlayerComparisonTable';
import { MAX_COMPARE_PLAYERS } from './useComparisonSlots';
import { usePlayerComparisonState } from './usePlayerComparisonState';
import './PlayerComparison.css';

export default function PlayerComparison({ onPlayerClick, onPlayerSeasonClick }) {
  const {
    comparisonSlots,
    selectionError,
    playerOptionsLoading,
    playerOptionsError,
    playerOptions,
    selectedPlayers,
    comparisonProfileLabel,
    comparisonRows,
    statWinnersByKey,
    weeksWinners,
    winCountsBySlot,
    handlePlayerSelect,
    handleSeasonChange,
    handleRemovePlayer,
  } = usePlayerComparisonState();

  return (
    <div className="direct-comparison-container">
      <div className="direct-comparison-stage">
        <PlayerComparisonHeader
          comparisonProfileLabel={comparisonProfileLabel}
          selectedCount={selectedPlayers.length}
          maxPlayers={MAX_COMPARE_PLAYERS}
        />
        <PlayerComparisonSlotsPanel
          comparisonSlots={comparisonSlots}
          playerOptionsLoading={playerOptionsLoading}
          playerOptionsError={playerOptionsError}
          selectionError={selectionError}
          playerOptions={playerOptions}
          onPlayerSelect={handlePlayerSelect}
          onSeasonChange={handleSeasonChange}
          onRemovePlayer={handleRemovePlayer}
        />

        <div className="direct-comparison-panel direct-comparison-panel--table">
          <h2>Comparison Table</h2>
          <PlayerComparisonTable
            selectedPlayers={selectedPlayers}
            comparisonRows={comparisonRows}
            statWinnersByKey={statWinnersByKey}
            weeksWinners={weeksWinners}
            winCountsBySlot={winCountsBySlot}
            onPlayerClick={onPlayerClick}
            onPlayerSeasonClick={onPlayerSeasonClick}
          />
        </div>
      </div>
    </div>
  );
}
