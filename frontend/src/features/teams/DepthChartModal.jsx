/**
 * File overview: Component for Depth Chart Modal within the teams feature.
 */

import { getTeamDepthChart } from '../../api';
import { useTeamModalData } from '../../shared/hooks/useTeamModalData';
import { getTeamColor } from '../../shared/utils/teamColors';
import { DepthChartTable, ModalBackdrop } from '../../shared/ui';
import './DepthChartModal.css';

export default function DepthChartModal({ team, onClose, onPlayerClick }) {
  const { data: depthChart, loading, error } = useTeamModalData(team, getTeamDepthChart, 'Failed to load depth chart');
  const teamHeaderColor = { color: getTeamColor(depthChart?.team || team) };
  const handlePlayerClick = (playerName) => {
    if (!playerName) return;
    onClose?.();
    onPlayerClick?.(playerName);
  };

  if (!team) return null;

  return (
    <ModalBackdrop onClose={onClose}>
      <div className="depth-chart-modal-content">
        <button className="depth-chart-close-button" onClick={onClose}>
          ×
        </button>
        {loading && <div className="loading">Loading depth chart...</div>}
        {error && <div className="error">{error}</div>}
        {depthChart && !loading && (
          <>
            <div className="depth-chart-header">
              <h2 className="depth-chart-title" style={teamHeaderColor}>
                {depthChart.team}
              </h2>
              <p className="depth-chart-full-name">{depthChart.team_name}</p>
            </div>
            <div className="depth-chart-table-wrapper">
              <DepthChartTable entries={depthChart.depth_chart} onPlayerClick={onPlayerClick ? handlePlayerClick : undefined} />
            </div>
          </>
        )}
      </div>
    </ModalBackdrop>
  );
}
