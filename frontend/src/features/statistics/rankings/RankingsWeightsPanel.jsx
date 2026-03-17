import { getStatLabel } from '../../../shared/utils/statDefinitions';
import { DEFAULT_CATEGORY_WEIGHT, DEFAULT_STAT_WEIGHT } from './rankingsHelpers';
import { RANKING_PRESETS } from './rankingPresets';
import WeightScale from './WeightScale';

export default function RankingsWeightsPanel({rankableGroups, selectedPreset, handlePresetChange, resetPositionWeights, categoryWeights, expandedCategories, toggleCategoryDetails, setCategoryWeight, statWeights, setStatWeight}) {
  return (
    <div className="rankings-panel rankings-panel--weights">
      <div className="rankings-section-header">
        <h2>Weight Controls</h2>
        <div className="preset-control">
          <label htmlFor="rankings-preset-select">Preset</label>
          <select id="rankings-preset-select" value={selectedPreset} onChange={(e) => handlePresetChange(e.target.value, rankableGroups)}>
            {RANKING_PRESETS.map((preset) => (<option key={preset.id} value={preset.id}>{preset.label}</option>))}
          </select>
        </div>
        <button type="button" className="reset-weights-button" onClick={resetPositionWeights}>Reset Weights</button>
      </div>

      {rankableGroups.map(({ category, stats }) => {
        const categoryWeight = categoryWeights[category] ?? DEFAULT_CATEGORY_WEIGHT;
        const expanded = Boolean(expandedCategories[category]);
        return (
          <div key={category} className="weight-category">
            <div className="weight-category-header">
              <h3>{category}</h3>
              <button type="button" className="weight-details-toggle" onClick={() => toggleCategoryDetails(category)}>{expanded ? 'Hide Stats' : 'Individual'}</button>
            </div>

            <WeightScale value={categoryWeight} onChange={(value) => setCategoryWeight(category, value)} ariaLabel={`${category} category weight`}/>

            {expanded && (
              <div className="weight-stats-list">
                {stats.map((stat) => (
                  <div key={stat} className="weight-stat-row">
                    <span>{getStatLabel(stat)}</span>
                    <WeightScale compact value={statWeights[stat] ?? DEFAULT_STAT_WEIGHT} onChange={(value) => setStatWeight(stat, value)} ariaLabel={`${getStatLabel(stat)} stat weight`}/>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
