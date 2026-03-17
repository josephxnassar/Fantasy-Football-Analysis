import DepthChartModal from './DepthChartModal';
import TeamBrowser from './TeamBrowser';

function DepthCharts({ onPlayerClick }) {
  return (
    <TeamBrowser
      actionLabel="View Depth Chart →"
      renderModal={(team, onClose) => <DepthChartModal team={team} onClose={onClose} onPlayerClick={onPlayerClick} />}
    />
  );
}

export default DepthCharts;
