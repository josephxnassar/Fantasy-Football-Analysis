import { getStatLabel } from '../../utils/statDefinitions';
import { TOP_N_OPTIONS } from '../../utils/uiOptions';
import { POSITION_OPTIONS } from './chartsHelpers';

export default function ChartControls({
  position,
  setPosition,
  chartData,
  season,
  setSeason,
  stat,
  setStat,
  statOptions,
  topN,
  setTopN,
}) {
  // Fully controlled filter row; parent owns all chart state.
  return (
    <div className="charts-controls">
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
        <label>Stat:</label>
        <select value={stat} onChange={(e) => setStat(e.target.value)}>
          {statOptions.map(({ category, stats }) => (
            <optgroup key={category} label={category}>
              {stats.map((option) => (
                <option key={option} value={option}>
                  {getStatLabel(option)}
                </option>
              ))}
            </optgroup>
          ))}
        </select>
      </div>

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
  );
}
