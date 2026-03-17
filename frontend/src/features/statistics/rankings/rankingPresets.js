export const RANKING_PRESETS = [
  { id: 'balanced', label: 'Balanced' },
  { id: 'volume', label: 'Volume' },
  { id: 'efficiency', label: 'Efficiency' },
  { id: 'upside', label: 'Upside' },
];

function getPresetWeight(category, presetId) {
  const name = String(category || '').toLowerCase();

  if (presetId === 'balanced') return 1;

  if (presetId === 'volume') {
    if (name.includes('volume') || name.includes('workload') || name.includes('opportunity')) return 2;
    if (name.includes('efficiency')) return 0;
    if (name.includes('risk')) return 0;
    return 1;
  }

  if (presetId === 'efficiency') {
    if (name.includes('efficiency') || name.includes('accuracy') || name.includes('separation')) return 2;
    if (name.includes('volume') || name.includes('workload') || name.includes('opportunity')) return 0;
    return 1;
  }

  // upside
  if (name.includes('production') || name.includes('impact') || name.includes('yardage') || name.includes('bonus')) return 2;
  if (name.includes('efficiency') || name.includes('separation')) return 1;
  if (name.includes('risk')) return 0;
  return 1;
}

export function buildPresetProfile(presetId, rankableGroups) {
  const categoryWeights = Object.fromEntries(rankableGroups.map(({ category }) => [category, getPresetWeight(category, presetId)]));
  return { categoryWeights, statWeights: {} };
}
