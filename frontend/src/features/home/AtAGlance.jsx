/**
 * File overview: Component for At A Glance within the home feature.
 */

// Summary stat tiles showing app data coverage.

import { ErrorMessage, LoadingMessage } from '../../shared/ui';
import { useAppInfo } from './useAppInfo';
import './AtAGlance.css';

export default function AtAGlance() {
  const { data: appInfo, loading, error } = useAppInfo();

  if (loading) {
    return (
      <section className="landing-section">
        <h2 className="section-heading">At a Glance</h2>
        <LoadingMessage message="Loading app info..." />
      </section>
    );
  }

  if (error) {
    return (
      <section className="landing-section">
        <h2 className="section-heading">At a Glance</h2>
        <ErrorMessage message={error} />
      </section>
    );
  }

  if (!appInfo) return null;

  return (
    <section className="landing-section">
      <h2 className="section-heading">At a Glance</h2>
      <div className="landing-stats-grid">
        <div className="stat-tile">
          <span className="stat-tile-value">{appInfo.total_players.toLocaleString()}</span>
          <span className="stat-tile-label">Players Tracked</span>
        </div>
        <div className="stat-tile">
          <span className="stat-tile-value">{appInfo.current_season_players.toLocaleString()}</span>
          <span className="stat-tile-label">{appInfo.current_season} Active Players</span>
        </div>
        <div className="stat-tile">
          <span className="stat-tile-value">{appInfo.seasons.length}</span>
          <span className="stat-tile-label">
            Seasons ({appInfo.seasons[0]}–{appInfo.current_season})
          </span>
        </div>
        <div className="stat-tile">
          <span className="stat-tile-value">{appInfo.total_game_logs.toLocaleString()}</span>
          <span className="stat-tile-label">Weekly Game Logs</span>
        </div>
        <div className="stat-tile">
          <span className="stat-tile-value">{appInfo.stat_columns}</span>
          <span className="stat-tile-label">Stats Per Player</span>
        </div>
        <div className="stat-tile">
          <span className="stat-tile-value">{appInfo.rookie_count}</span>
          <span className="stat-tile-label">Rookies</span>
        </div>
      </div>
    </section>
  );
}
