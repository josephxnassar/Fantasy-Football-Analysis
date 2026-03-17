/**
 * File overview: Component for Rankings Header within the rankings feature.
 */

import { StatTooltip } from '../../../shared/ui';

export default function RankingsHeader({ season, setSeason, availableSeasons, currentSeason }) {
  return (
    <div className="rankings-panel rankings-panel--header">
      <div className="rankings-copy">
        <div className="rankings-kicker-with-help">
          <p className="rankings-kicker">Custom Weights</p>
          <StatTooltip
            label="Custom Weights"
            description="Set category and stat priorities on a -2 to +2 scale to build an overall cross-position ranking."
            iconSize={14}
          />
        </div>
        <h1>Player Rankings</h1>
      </div>

      <div className="rankings-controls">
        {availableSeasons?.length > 1 && (
          <div className="control-group">
            <label>Season:</label>
            <select value={season ?? currentSeason} onChange={(e) => setSeason(Number(e.target.value))}>
              {availableSeasons.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>
    </div>
  );
}
