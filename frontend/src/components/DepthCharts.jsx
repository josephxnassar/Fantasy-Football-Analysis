import TeamBrowser from './TeamBrowser';
import DepthChartModal from './DepthChartModal';

function DepthCharts({ onPlayerClick }) {
  return (
    <TeamBrowser
      actionLabel="View Depth Chart →"
      renderModal={(team, onClose) => (
        <DepthChartModal
          team={team}
          onClose={onClose}
          onPlayerClick={onPlayerClick}
        />
      )}
    />
  );
}

export default DepthCharts;
