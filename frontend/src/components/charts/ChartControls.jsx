import { getStatLabel } from '../../utils/statDefinitions';
import { CHART_VIEW_OPTIONS, TOP_N_OPTIONS, POSITION_OPTIONS } from './chartsConfig';

export default function ChartControls({
  view,
  setView,
  position,
  setPosition,
  chartData,
  season,
  setSeason,
  stat,
  setStat,
  statOptions,
  showStatControl = true,
  trendPlayer,
  setTrendPlayer,
  trendPlayerOptions = [],
  showTrendPlayerControl = false,
  topN,
  setTopN,
  showTopNControl = true,
}) {
  // Fully controlled filter row; parent owns all chart state.
  return (
    <div className="charts-controls">
      <div className="control-group">
        <label>View:</label>
        <select value={view} onChange={(e) => setView(e.target.value)}>
          {CHART_VIEW_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

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

      {showTrendPlayerControl && (
        <div className="control-group">
          <label>Player:</label>
          <select value={trendPlayer} onChange={(e) => setTrendPlayer(e.target.value)} disabled={!trendPlayerOptions.length}>
            {!trendPlayerOptions.length ? (
              <option value="">No qualifying players</option>
            ) : (
              trendPlayerOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))
            )}
          </select>
        </div>
      )}

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

      {showStatControl && (
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
      )}

      {showTopNControl && (
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
      )}
    </div>
  );
}
