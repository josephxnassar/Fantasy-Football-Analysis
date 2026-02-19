import { getTeamDepthChart } from '../api';
import { useTeamModalData } from '../hooks/useTeamModalData';
import { DepthChartTable } from './common';
import './DepthChartModal.css';

export default function DepthChartModal({ team, onClose }) {
  const { data: depthChart, loading, error } = useTeamModalData(team, getTeamDepthChart, 'Failed to load depth chart');

  if (!team) return null;

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="depth-chart-modal-overlay" onClick={handleOverlayClick}>
      <div className="depth-chart-modal-content">
        <button className="depth-chart-close-button" onClick={onClose}>×</button>

        {loading && <div className="loading">Loading depth chart...</div>}

        {error && <div className="error">{error}</div>}

        {depthChart && !loading && (
          <>
            <div className="depth-chart-header">
              <h2 className="depth-chart-title">{depthChart.team}</h2>
              <p className="depth-chart-full-name">{depthChart.team_name}</p>
            </div>

            <div className="depth-chart-table-wrapper">
              <DepthChartTable entries={depthChart.depth_chart} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
