/* Side-by-side player and season comparison using production stat metadata. */

import { useMemo, useRef, useState } from 'react';

import { getPlayer } from '../api';
import { useChartData } from '../hooks/useChartData';
import { POSITION_OPTIONS } from '../utils/leaderboardOptions';
import { formatStatForDisplay, getStatDefinition, getStatLabel } from '../utils/statDefinitions';
import { EmptyStateMessage, ErrorMessage, LoadingMessage, StatTooltip } from './common';
import {
  buildComparisonRows,
  buildComparisonWins,
  getWinningSlotIdsForStat,
  getWinningSlotIdsForWeeks,
} from './comparison/comparisonHelpers';
import './PlayerComparison.css';

const MAX_COMPARE_PLAYERS = 3;
const EMPTY_SLOT = {
  playerName: '',
  team: null,
  position: null,
  season: null,
  weeksPlayed: null,
  availableSeasons: [],
  stats: null,
  loading: false,
  error: null,
};

function createInitialSlots() {
  return Array.from({ length: MAX_COMPARE_PLAYERS }, (_, index) => ({
    id: index + 1,
    ...EMPTY_SLOT,
  }));
}

function isMissingStatValue(value) {
  return value === null || value === undefined || (typeof value === 'number' && Number.isNaN(value));
}

function formatComparisonValue(statKey, value) {
  if (isMissingStatValue(value)) return '—';
  return formatStatForDisplay(statKey, value);
}

export default function PlayerComparison({ onPlayerClick }) {
  const [positionProfile, setPositionProfile] = useState('Overall');
  const [comparisonSlots, setComparisonSlots] = useState(createInitialSlots);
  const [selectionError, setSelectionError] = useState(null);
  const requestIdsBySlotRef = useRef({});
  const { chartData, loading: playerOptionsLoading, error: playerOptionsError } = useChartData(positionProfile, null);

  const comparisonRows = buildComparisonRows(positionProfile);
  const playerOptions = useMemo(() => {
    const players = chartData?.players || [];
    return players
      .map((player) => player.name)
      .filter(Boolean)
      .sort((a, b) => a.localeCompare(b));
  }, [chartData?.players]);
  const selectedPlayers = comparisonSlots.filter((slot) => Boolean(slot.playerName));
  const statWinnersByKey = useMemo(
    () =>
      Object.fromEntries(
        comparisonRows
          .filter((row) => row.type === 'stat')
          .map((row) => [row.statKey, getWinningSlotIdsForStat(row.statKey, selectedPlayers)])
      ),
    [comparisonRows, selectedPlayers]
  );
  const weeksWinners = useMemo(
    () => getWinningSlotIdsForWeeks(selectedPlayers),
    [selectedPlayers]
  );
  const winCountsBySlot = useMemo(
    () => buildComparisonWins(comparisonRows, selectedPlayers),
    [comparisonRows, selectedPlayers]
  );

  const updateSlot = (slotId, updater) => {
    setComparisonSlots((previous) =>
      previous.map((slot) => (slot.id === slotId ? updater(slot) : slot))
    );
  };

  const clearSlot = (slotId) => {
    delete requestIdsBySlotRef.current[slotId];
    updateSlot(slotId, () => ({ id: slotId, ...EMPTY_SLOT }));
  };

  const getWeeksPlayedForSeason = (weeklyStats, season) => {
    if (!Array.isArray(weeklyStats) || season === null || season === undefined) return null;
    return weeklyStats.filter((week) => Number(week?.season) === Number(season)).length;
  };

  const loadPlayerDetails = async (slotId, playerName, season = null) => {
    const requestId = (requestIdsBySlotRef.current[slotId] || 0) + 1;
    requestIdsBySlotRef.current[slotId] = requestId;

    updateSlot(slotId, (slot) => ({ ...slot, playerName, loading: true, error: null }));

    try {
      const response = await getPlayer(playerName, season);
      if (requestIdsBySlotRef.current[slotId] !== requestId) return;

      const payload = response.data;
      const availableSeasons = payload.available_seasons || [];
      const resolvedSeason = season ?? (availableSeasons[0] ?? null);
      const weeksPlayed = getWeeksPlayedForSeason(payload.weekly_stats || [], resolvedSeason);

      updateSlot(slotId, (slot) => ({
        ...slot,
        playerName: payload.name,
        team: payload.team,
        position: payload.position,
        season: resolvedSeason,
        weeksPlayed,
        availableSeasons,
        stats: payload.stats || {},
        loading: false,
        error: null,
      }));
    } catch (err) {
      if (requestIdsBySlotRef.current[slotId] !== requestId) return;
      const message = err?.message || 'Failed to load player details.';
      updateSlot(slotId, (slot) => ({
        ...slot,
        loading: false,
        error: message,
      }));
    }
  };

  const handlePositionProfileChange = (nextPosition) => {
    setPositionProfile(nextPosition);
    setSelectionError(null);
    requestIdsBySlotRef.current = {};
    setComparisonSlots(createInitialSlots());
  };

  const handlePlayerSelect = (slotId, playerName) => {
    setSelectionError(null);
    if (!playerName) {
      clearSlot(slotId);
      return;
    }

    const duplicate = comparisonSlots.some((slot) => slot.id !== slotId && slot.playerName === playerName);
    if (duplicate) {
      setSelectionError('Each slot must use a different player.');
      return;
    }

    void loadPlayerDetails(slotId, playerName, null);
  };

  const handleSeasonChange = (slotId, nextSeasonValue) => {
    const slot = comparisonSlots.find((candidate) => candidate.id === slotId);
    const nextSeason = Number(nextSeasonValue);
    if (!slot || !slot.playerName || Number.isNaN(nextSeason)) return;
    void loadPlayerDetails(slotId, slot.playerName, nextSeason);
  };

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
          {selectedPlayers.length === 0 ? (
            <EmptyStateMessage message="Select at least one player to compare." />
          ) : (
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
                      const displayValue = slot.loading
                        ? '...'
                        : (slot.weeksPlayed ?? '—');
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
          )}
        </div>
      </div>
    </div>
  );
}
