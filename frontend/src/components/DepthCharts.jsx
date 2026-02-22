import TeamBrowser from './TeamBrowser';
import DepthChartModal from './DepthChartModal';

function DepthCharts() {
  return (
    <TeamBrowser
      actionLabel="View Depth Chart →"
      // TeamBrowser owns selection; this injects the team-specific modal.
      renderModal={(team, onClose) => (
        <DepthChartModal team={team} onClose={onClose} />
      )}
    />
  );
}

export default DepthCharts;
