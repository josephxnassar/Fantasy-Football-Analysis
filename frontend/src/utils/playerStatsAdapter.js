/* Normalize player details payload to canonical stat keys for modal rendering. */

import { normalizeStatsRecord } from './statDefinitions';

const AGGREGATE_CONTEXT_FIELDS = ['season', 'player_id', 'player_display_name', 'position', 'team'];
const WEEKLY_CONTEXT_FIELDS = ['season', 'week', 'game_id', 'player_id', 'player_display_name', 'position', 'team', 'opponent_team'];

function pickContext(record, fields) {
  const out = {};
  fields.forEach((field) => {
    if (record && Object.prototype.hasOwnProperty.call(record, field)) {
      out[field] = record[field];
    }
  });
  return out;
}

function adaptRecord(record, contextFields) {
  return {
    ...pickContext(record, contextFields),
    ...normalizeStatsRecord(record),
  };
}

export function adaptPlayerDetailsForDisplay(playerDetails) {
  if (!playerDetails) return playerDetails;

  const adaptedStats = adaptRecord(playerDetails.stats || {}, AGGREGATE_CONTEXT_FIELDS);
  const adaptedWeekly = Array.isArray(playerDetails.weekly_stats)
    ? playerDetails.weekly_stats.map((week) => adaptRecord(week, WEEKLY_CONTEXT_FIELDS))
    : [];

  return {
    ...playerDetails,
    stats: adaptedStats,
    weekly_stats: adaptedWeekly,
  };
}
