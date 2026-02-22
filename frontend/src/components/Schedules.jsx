import TeamBrowser from './TeamBrowser';
import TeamScheduleModal from './TeamScheduleModal';

function Schedules() {
  return (
    <TeamBrowser
      actionLabel="View Schedule →"
      // TeamBrowser owns selection; this injects the team-specific modal.
      renderModal={(team, onClose) => (
        <TeamScheduleModal team={team} onClose={onClose} />
      )}
    />
  );
}

export default Schedules;
