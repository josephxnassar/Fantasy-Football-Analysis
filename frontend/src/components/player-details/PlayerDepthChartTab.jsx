import { DepthChartTable } from '../common';

export default function PlayerDepthChartTab({ depthChartLoading, teamDepthChart, playerName }) {
  return (
    <div className="modal-depth-chart-content">
      {depthChartLoading && (
        <div className="loading">Loading depth chart...</div>
      )}
      {/* Mini table highlights the selected player inside their team depth chart. */}
      {!depthChartLoading && teamDepthChart && teamDepthChart.depth_chart.length > 0 && (
        <>
          <h3>{teamDepthChart.team_name} Depth Chart</h3>
          <DepthChartTable
            entries={teamDepthChart.depth_chart}
            variant="mini"
            highlightName={playerName}
          />
        </>
      )}
      {!depthChartLoading && (!teamDepthChart || teamDepthChart.depth_chart.length === 0) && (
        <p className="player-details-no-data">No depth chart available</p>
      )}
    </div>
  );
}
