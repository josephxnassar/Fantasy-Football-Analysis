/**
 * File overview: Component for Team Schedule Modal within the teams feature.
 */

import { useCallback, useRef, useState } from 'react';
import { getTeamSchedule } from '../../api';
import { useTeamModalData } from '../../shared/hooks/useTeamModalData';
import { getTeamColor } from '../../shared/utils/teamColors';
import { ModalBackdrop } from '../../shared/ui';
import TeamScheduleGameCard from './TeamScheduleGameCard';
import TeamScheduleHeader from './TeamScheduleHeader';
import './TeamScheduleModal.css';

export default function TeamScheduleModal({ team, onClose }) {
  const [selectedSeason, setSelectedSeason] = useState(null);
  const [expandedWeek, setExpandedWeek] = useState(null);
  const prevTeamRef = useRef(team);

  const fetchSchedule = useCallback(
    (t) => {
      if (t !== prevTeamRef.current) {
        prevTeamRef.current = t;
        setSelectedSeason(null);
        setExpandedWeek(null);
        return getTeamSchedule(t, null);
      }
      return getTeamSchedule(t, selectedSeason);
    },
    [selectedSeason],
  );

  const { data: schedule, loading, error } = useTeamModalData(team, fetchSchedule, 'Failed to load schedule');
  const scheduleTeamColor = getTeamColor(schedule?.team || team);
  const teamHeaderColor = { color: scheduleTeamColor };

  const handleSeasonChange = (event) => {
    setSelectedSeason(Number(event.target.value));
    setExpandedWeek(null);
  };

  const toggleGameDetails = (week, isBye) => {
    if (isBye) return;
    setExpandedWeek((previousWeek) => (previousWeek === week ? null : week));
  };

  if (!team) return null;

  return (
    <ModalBackdrop onClose={onClose}>
      <div className="schedule-modal-content">
        <button className="schedule-close-button" onClick={onClose}>
          ×
        </button>
        {loading && <div className="loading">Loading schedule...</div>}
        {error && <div className="error">{error}</div>}
        {schedule && !loading && (
          <>
            <TeamScheduleHeader
              schedule={schedule}
              selectedSeason={selectedSeason}
              onSeasonChange={handleSeasonChange}
              teamHeaderColor={teamHeaderColor}
            />
            <div className="schedule-grid">
              {schedule.schedule.map((game) => (
                <TeamScheduleGameCard
                  key={game.week}
                  game={game}
                  team={schedule.team}
                  teamColor={scheduleTeamColor}
                  expanded={expandedWeek === game.week}
                  onToggle={toggleGameDetails}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </ModalBackdrop>
  );
}
