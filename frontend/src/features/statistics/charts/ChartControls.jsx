/**
 * File overview: Component for Chart Controls within the statistics charts feature.
 */

import { getStatLabel } from '../../../shared/utils/statDefinitions';
import { POSITION_OPTIONS } from '../statisticsOptions';
import { CHART_VIEW_OPTIONS } from './ChartsMeta';

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
  showPositionControl = true,
  showSeasonControl = true,
  trendPlayer,
  setTrendPlayer,
  trendPlayerOptions = [],
  showTrendPlayerControl = false,
}) {
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

      {showPositionControl && (
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
      )}

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

      {showSeasonControl && chartData?.available_seasons?.length > 1 && (
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
    </div>
  );
}
