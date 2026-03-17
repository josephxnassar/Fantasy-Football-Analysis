import { POSITION_OPTIONS } from '../statisticsOptions';
import { StatTooltip } from '../../../shared/ui';

export default function RankingsHeader({ position, setPosition, season, setSeason, availableSeasons, currentSeason }) {
  return (
    <div className="rankings-panel rankings-panel--header">
      <div className="rankings-copy">
        <div className="rankings-kicker-with-help">
          <p className="rankings-kicker">Custom Weights</p>
          <StatTooltip
            label="Custom Weights"
            description="Set category and stat priorities on a -2 to +2 scale. Category and stat weights both shape the final rank."
            iconSize={14}
          />
        </div>
        <h1>Player Rankings</h1>
      </div>

      <div className="rankings-controls">
        <div className="control-group">
          <label className="control-label-with-help">
            <span>Position:</span>
            <StatTooltip
              label="Overall vs Position"
              description="Overall is a cross-position score, so ordering can differ from position-specific views."
            />
          </label>
          <select value={position} onChange={(e) => setPosition(e.target.value)}>
            {POSITION_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

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
