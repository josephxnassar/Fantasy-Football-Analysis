/* Weighted rankings tab with category + stat-level controls. */

import { useEffect, useMemo, useState } from 'react';

import { useChartData } from '../hooks/useChartData';
import { POSITION_OPTIONS, TOP_N_OPTIONS } from '../utils/leaderboardOptions';
import { RANKING_GROUPS } from '../utils/rankingMeta';
import { getStatLabel } from '../utils/statDefinitions';
import { ErrorMessage, LoadingMessage } from './common';
import {
  buildRankings,
  DEFAULT_CATEGORY_WEIGHT,
  DEFAULT_STAT_WEIGHT,
  getRankableGroups,
} from './rankings/rankingsHelpers';
import { buildPresetProfile, RANKING_PRESETS } from './rankings/rankingPresets';
import WeightScale from './rankings/WeightScale';
import './Rankings.css';

const STORAGE_KEY = 'rankingsWeightsV1';
const EMPTY_WEIGHTS = Object.freeze({});

function loadWeightProfiles() {
  if (typeof window === 'undefined') return {};
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' ? parsed : {};
  } catch {
    return {};
  }
}

export default function Rankings({ onPlayerClick }) {
  const [position, setPosition] = useState('Overall');
  const [season, setSeason] = useState(null);
  const [topN, setTopN] = useState(20);
  const [selectedPreset, setSelectedPreset] = useState('balanced');
  const [expandedCategories, setExpandedCategories] = useState({});
  const [weightProfiles, setWeightProfiles] = useState(loadWeightProfiles);

  const { chartData, loading, error } = useChartData(position, season);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(weightProfiles));
  }, [weightProfiles]);

  const rankableGroups = useMemo(
    () => getRankableGroups(position, chartData?.stat_columns || [], RANKING_GROUPS),
    [position, chartData?.stat_columns]
  );

  const currentProfile = weightProfiles[position] || {};
  const categoryWeights = currentProfile.categoryWeights || EMPTY_WEIGHTS;
  const statWeights = currentProfile.statWeights || EMPTY_WEIGHTS;

  const rankedPlayers = useMemo(
    () => buildRankings(chartData?.players || [], rankableGroups, categoryWeights, statWeights, topN),
    [chartData?.players, rankableGroups, categoryWeights, statWeights, topN]
  );

  const updateProfile = (updater) => {
    setWeightProfiles((previous) => {
      const profile = previous[position] || { categoryWeights: {}, statWeights: {} };
      const nextProfile = updater(profile);
      return { ...previous, [position]: nextProfile };
    });
  };

  const setCategoryWeight = (category, value) => {
    updateProfile((profile) => ({
      ...profile,
      categoryWeights: {
        ...profile.categoryWeights,
        [category]: value,
      },
    }));
  };

  const setStatWeight = (stat, value) => {
    updateProfile((profile) => ({
      ...profile,
      statWeights: {
        ...profile.statWeights,
        [stat]: value,
      },
    }));
  };

  const resetPositionWeights = () => {
    setWeightProfiles((previous) => {
      const next = { ...previous };
      delete next[position];
      return next;
    });
  };

  const toggleCategoryDetails = (category) => {
    setExpandedCategories((previous) => ({
      ...previous,
      [category]: !previous[category],
    }));
  };

  const handlePresetChange = (presetId) => {
    setSelectedPreset(presetId);
    if (!rankableGroups.length) return;
    updateProfile(() => buildPresetProfile(presetId, rankableGroups));
  };

  if (loading) return <LoadingMessage message="Loading ranking data..." />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="rankings-container">
      <div className="rankings-stage">
        <div className="rankings-panel rankings-panel--header">
          <div className="rankings-copy">
            <p className="rankings-kicker">Custom Weights</p>
            <h1>Player Rankings</h1>
            <p className="rankings-description">
              Set category and stat priorities on a -2 to +2 scale. Category and stat weights both shape the final rank.
            </p>
          </div>

          <div className="rankings-controls">
            <div className="control-group">
              <label>Position:</label>
              <select value={position} onChange={(e) => setPosition(e.target.value)}>
                {POSITION_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>

            {chartData?.available_seasons?.length > 1 && (
              <div className="control-group">
                <label>Season:</label>
                <select value={season ?? chartData.season} onChange={(e) => setSeason(Number(e.target.value))}>
                  {chartData.available_seasons.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="control-group">
              <label>Show:</label>
              <select value={topN} onChange={(e) => setTopN(Number(e.target.value))}>
                {TOP_N_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    Top {option}
                  </option>
                ))}
              </select>
            </div>

          </div>
        </div>

        <div className="rankings-body">
          <div className="rankings-panel rankings-panel--weights">
            <div className="rankings-section-header">
              <h2>Weight Controls</h2>
              <div className="preset-control">
                <label htmlFor="rankings-preset-select">Preset</label>
                <select
                  id="rankings-preset-select"
                  value={selectedPreset}
                  onChange={(e) => handlePresetChange(e.target.value)}
                >
                  {RANKING_PRESETS.map((preset) => (
                    <option key={preset.id} value={preset.id}>
                      {preset.label}
                    </option>
                  ))}
                </select>
              </div>
              <button type="button" className="reset-weights-button" onClick={resetPositionWeights}>
                Reset Weights
              </button>
            </div>
            {rankableGroups.map(({ category, stats }) => {
              const categoryWeight = categoryWeights[category] ?? DEFAULT_CATEGORY_WEIGHT;
              const expanded = Boolean(expandedCategories[category]);
              return (
                <div key={category} className="weight-category">
                  <div className="weight-category-header">
                    <h3>{category}</h3>
                    <button
                      type="button"
                      className="weight-details-toggle"
                      onClick={() => toggleCategoryDetails(category)}
                    >
                      {expanded ? 'Hide Stats' : 'Individual'}
                    </button>
                  </div>

                  <WeightScale
                    value={categoryWeight}
                    onChange={(value) => setCategoryWeight(category, value)}
                    ariaLabel={`${category} category weight`}
                  />

                  {expanded && (
                    <div className="weight-stats-list">
                      {stats.map((stat) => (
                        <div key={stat} className="weight-stat-row">
                          <span>{getStatLabel(stat)}</span>
                          <WeightScale
                            compact
                            value={statWeights[stat] ?? DEFAULT_STAT_WEIGHT}
                            onChange={(value) => setStatWeight(stat, value)}
                            ariaLabel={`${getStatLabel(stat)} stat weight`}
                          />
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="rankings-panel rankings-panel--results">
            <h2>Results</h2>
            {rankedPlayers.length === 0 ? (
              <p className="rankings-empty">No players qualify for the current settings.</p>
            ) : (
              <div className="rankings-table-wrapper">
                <table className="rankings-table">
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Player</th>
                      <th>Team</th>
                      <th>Pos</th>
                      <th>Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rankedPlayers.map((player) => {
                      const scoreValue = player.score * 100;
                      return (
                        <tr key={`${player.name}-${player.rank}`}>
                          <td>{player.rank}</td>
                          <td>
                            <button
                              type="button"
                              className="ranking-player-button"
                              onClick={() => onPlayerClick?.(player.name)}
                            >
                              {player.name}
                            </button>
                          </td>
                          <td>{player.team || '-'}</td>
                          <td>{player.position || '-'}</td>
                          <td className={scoreValue >= 0 ? 'score-positive' : 'score-negative'}>
                            {scoreValue > 0 ? '+' : ''}
                            {scoreValue.toFixed(1)}
                          </td>
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
    </div>
  );
}
