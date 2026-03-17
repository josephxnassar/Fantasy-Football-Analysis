/**
 * File overview: Rankings state hook that stores one overall weights profile, preset choice, and expanded UI state.
 */

import { useEffect, useState } from 'react';

import { useSessionStorageObject } from '../../../shared/hooks/useSessionStorageObject';
import { buildPresetProfile } from './rankingPresets';

const STORAGE_KEY = 'rankingsWeights';
const UI_STORAGE_KEY = 'rankingsUi';
const EMPTY_WEIGHTS = Object.freeze({});

function isObject(value) {
  return Boolean(value) && typeof value === 'object';
}

function normalizeStoredWeights(storedWeights) {
  return {
    categoryWeights: isObject(storedWeights?.categoryWeights) ? storedWeights.categoryWeights : EMPTY_WEIGHTS,
    statWeights: isObject(storedWeights?.statWeights) ? storedWeights.statWeights : EMPTY_WEIGHTS,
  };
}

function toStoredWeights({ categoryWeights = EMPTY_WEIGHTS, statWeights = EMPTY_WEIGHTS }) {
  if (Object.keys(categoryWeights).length === 0 && Object.keys(statWeights).length === 0) return {};
  return { categoryWeights, statWeights };
}

export function useRankingsState() {
  const [uiState, setUiState] = useSessionStorageObject(UI_STORAGE_KEY, {});
  const [storedWeights, setStoredWeights] = useSessionStorageObject(STORAGE_KEY, {});
  const [season, setSeason] = useState(null);
  const [selectedPreset, setSelectedPreset] = useState(uiState.selectedPreset || 'balanced');
  const [expandedCategories, setExpandedCategories] = useState({});

  useEffect(() => {
    setUiState({ selectedPreset });
  }, [selectedPreset, setUiState]);

  const { categoryWeights, statWeights } = normalizeStoredWeights(storedWeights);

  const updateWeights = (updater) => {
    // Rankings now has one flat overall weights object, so keep updates local to
    // category/stat weights instead of re-introducing profile indirection.
    setStoredWeights((previous) => toStoredWeights(updater(normalizeStoredWeights(previous))));
  };

  const setCategoryWeight = (category, value) => {
    updateWeights((weights) => ({ ...weights, categoryWeights: { ...weights.categoryWeights, [category]: value } }));
  };

  const setStatWeight = (stat, value) => {
    updateWeights((weights) => ({ ...weights, statWeights: { ...weights.statWeights, [stat]: value } }));
  };

  const resetWeights = () => {
    setStoredWeights({});
  };

  const toggleCategoryDetails = (category) => {
    setExpandedCategories((previous) => ({ ...previous, [category]: !previous[category] }));
  };

  const handlePresetChange = (presetId, rankableGroups) => {
    setSelectedPreset(presetId);
    if (!rankableGroups.length) return;
    updateWeights(() => buildPresetProfile(presetId, rankableGroups));
  };

  return {
    season,
    setSeason,
    selectedPreset,
    expandedCategories,
    categoryWeights,
    statWeights,
    setCategoryWeight,
    setStatWeight,
    resetWeights,
    toggleCategoryDetails,
    handlePresetChange,
  };
}
