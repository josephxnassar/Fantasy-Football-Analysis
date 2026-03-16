import { useEffect, useState } from 'react';

import { useSessionStorageObject } from '../../hooks/useSessionStorageObject';
import { buildPresetProfile } from './rankingPresets';

const STORAGE_KEY = 'rankingsWeights';
const UI_STORAGE_KEY = 'rankingsUi';
const EMPTY_WEIGHTS = Object.freeze({});

export function useRankingsState() {
  const [uiState, setUiState] = useSessionStorageObject(UI_STORAGE_KEY, {});
  const [weightProfiles, setWeightProfiles] = useSessionStorageObject(STORAGE_KEY, {});
  const [position, setPosition] = useState(uiState.position || 'Overall');
  const [season, setSeason] = useState(null);
  const [topN, setTopN] = useState(uiState.topN || 20);
  const [selectedPreset, setSelectedPreset] = useState(uiState.selectedPreset || 'balanced');
  const [expandedCategories, setExpandedCategories] = useState({});

  useEffect(() => {
    setUiState({ position, topN, selectedPreset });
  }, [position, topN, selectedPreset, setUiState]);

  const currentProfile = weightProfiles[position] || {};
  const categoryWeights = currentProfile.categoryWeights || EMPTY_WEIGHTS;
  const statWeights = currentProfile.statWeights || EMPTY_WEIGHTS;

  const updateProfile = (updater) => {
    setWeightProfiles((previous) => {
      const profile = previous[position] || { categoryWeights: {}, statWeights: {} };
      const nextProfile = updater(profile);
      return { ...previous, [position]: nextProfile };
    });
  };

  const setCategoryWeight = (category, value) => {
    updateProfile((profile) => ({...profile, categoryWeights: {...profile.categoryWeights, [category]: value}}));
  };

  const setStatWeight = (stat, value) => {
    updateProfile((profile) => ({...profile, statWeights: {...profile.statWeights, [stat]: value}}));
  };

  const resetPositionWeights = () => {
    setWeightProfiles((previous) => {
      const next = { ...previous };
      delete next[position];
      return next;
    });
  };

  const toggleCategoryDetails = (category) => {
    setExpandedCategories((previous) => ({...previous, [category]: !previous[category]}));
  };

  const handlePresetChange = (presetId, rankableGroups) => {
    setSelectedPreset(presetId);
    if (!rankableGroups.length)
      return;
    updateProfile(() => buildPresetProfile(presetId, rankableGroups));
  };

  return {
    position,
    setPosition,
    season,
    setSeason,
    topN,
    setTopN,
    selectedPreset,
    expandedCategories,
    categoryWeights,
    statWeights,
    setCategoryWeight,
    setStatWeight,
    resetPositionWeights,
    toggleCategoryDetails,
    handlePresetChange,
  };
}
