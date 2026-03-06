/* Side-by-side player and season comparison using production stat metadata. */

import { POSITION_OPTIONS } from '../utils/leaderboardOptions';
import { MAX_COMPARE_PLAYERS, usePlayerComparisonState } from './comparison/usePlayerComparisonState';
import { ErrorMessage, LoadingMessage } from './common';
import PlayerComparisonTable from './comparison/PlayerComparisonTable';
import './PlayerComparison.css';

export default function PlayerComparison({ onPlayerClick, onPlayerSeasonClick }) {
  const {
    positionProfile,
    comparisonSlots,
    selectionError,
    playerOptionsLoading,
    playerOptionsError,
    playerOptions,
    selectedPlayers,
    comparisonRows,
    statWinnersByKey,
    weeksWinners,
    winCountsBySlot,
    handlePositionProfileChange,
    handlePlayerSelect,
    handleSeasonChange,
  } = usePlayerComparisonState();

  return (
    <div className="direct-comparison-container">
      <div className="direct-comparison-stage">
        <div className="direct-comparison-panel direct-comparison-panel--header">
          <div className="direct-comparison-copy">
            <p className="direct-comparison-kicker">Player Comparison</p>
            <h1>Player Comparison</h1>
            <p className="direct-comparison-subtitle">
              Pick a position pool, choose up to {MAX_COMPARE_PLAYERS} players, then select each player&apos;s season.
            </p>
          </div>

          <div className="direct-comparison-controls">
            <div className="direct-comparison-control-group">
              <label>Position:</label>
              <select value={positionProfile} onChange={(event) => handlePositionProfileChange(event.target.value)}>
                {POSITION_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>
            <p className="direct-comparison-selection-count">
              {selectedPlayers.length} / {MAX_COMPARE_PLAYERS} selected
            </p>
          </div>
        </div>

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
                  <article key={slot.id} className="direct-comparison-slot-card">
                    <h3>Slot {slot.id}</h3>

                    <div className="direct-comparison-slot-field">
                      <label htmlFor={`comparison-player-${slot.id}`}>Player</label>
                      <select
                        id={`comparison-player-${slot.id}`}
                        value={slot.playerName}
                        onChange={(event) => handlePlayerSelect(slot.id, event.target.value)}
                        disabled={Boolean(playerOptionsError) || playerOptions.length === 0}
                      >
                        <option value="">Select player</option>
                        {playerOptions.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="direct-comparison-slot-field">
                      <label htmlFor={`comparison-season-${slot.id}`}>Season</label>
                      <select
                        id={`comparison-season-${slot.id}`}
                        value={slot.season ?? ''}
                        onChange={(event) => handleSeasonChange(slot.id, event.target.value)}
                        disabled={!slot.playerName || slot.loading || slot.availableSeasons.length === 0}
                      >
                        {!slot.playerName ? (
                          <option value="">Select player first</option>
                        ) : (
                          slot.availableSeasons.map((seasonOption) => (
                            <option key={seasonOption} value={seasonOption}>
                              {seasonOption}
                            </option>
                          ))
                        )}
                      </select>
                    </div>

                    <p className="direct-comparison-slot-meta">
                      {slot.playerName ? [slot.position, slot.team].filter(Boolean).join(' • ') : 'No player selected'}
                    </p>
                    {slot.loading && <p className="direct-comparison-player-status">Loading player data...</p>}
                    {slot.error && <p className="direct-comparison-player-error">{slot.error}</p>}
                  </article>
                ))}
              </div>
            </>
          )}
        </div>

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
