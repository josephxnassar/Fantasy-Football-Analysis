/* Shared sample-size thresholds for rate/efficiency stats. */

const PASS_ATTEMPT_VOLUME_STATS = ['pass_att', 'attempts', 'ng_pass_att', 'pfr_pass_pass_att', 'ffo_pass_att'];
const RUSH_ATTEMPT_VOLUME_STATS = ['rush_att', 'carries', 'ng_rush_rush_att', 'pfr_rush_att'];

export const STAT_THRESHOLDS = {
  'Yds/Rush': { volumeStats: ['rush_att', 'carries'], minVolume: 100 },
  'Yds/Rec': { volumeStats: ['rec', 'receptions'], minVolume: 50 },
  ng_rush_efficiency: { volumeStats: RUSH_ATTEMPT_VOLUME_STATS, minVolume: 100 },
  pfr_rush_yac_att: { volumeStats: RUSH_ATTEMPT_VOLUME_STATS, minVolume: 100 },
  pfr_rush_ybc_att: { volumeStats: RUSH_ATTEMPT_VOLUME_STATS, minVolume: 100 },
  receiving_epa: { volumeStats: ['targets'], minVolume: 50 },
  racr: { volumeStats: ['targets'], minVolume: 50 },
  pfr_rec_drop_pct: { volumeStats: ['targets', 'pfr_rec_tgt'], minVolume: 50 },
  ng_rec_avg_separation: { volumeStats: ['targets', 'ng_rec_targets'], minVolume: 50 },
  pfr_rec_adot: { volumeStats: ['targets', 'pfr_rec_tgt'], minVolume: 50 },
  ng_rec_catch_pct: { volumeStats: ['targets', 'ng_rec_targets'], minVolume: 50 },
  ng_rec_avg_yac: { volumeStats: ['rec', 'receptions', 'ng_rec_rec', 'pfr_rec_rec'], minVolume: 40 },
  ng_rec_avg_yac_above_expectation: { volumeStats: ['rec', 'receptions', 'ng_rec_rec', 'pfr_rec_rec'], minVolume: 40 },
  pfr_rec_yac_r: { volumeStats: ['rec', 'receptions', 'ng_rec_rec', 'pfr_rec_rec'], minVolume: 40 },
  passing_cpoe: { volumeStats: PASS_ATTEMPT_VOLUME_STATS, minVolume: 150 },
  pacr: { volumeStats: PASS_ATTEMPT_VOLUME_STATS, minVolume: 150 },
  ng_pass_passer_rating: { volumeStats: PASS_ATTEMPT_VOLUME_STATS, minVolume: 150 },
  ng_pass_avg_time_to_throw: { volumeStats: PASS_ATTEMPT_VOLUME_STATS, minVolume: 150 },
  pfr_pass_bad_throw_pct: { volumeStats: PASS_ATTEMPT_VOLUME_STATS, minVolume: 150 },
  pfr_pass_on_tgt_pct: { volumeStats: PASS_ATTEMPT_VOLUME_STATS, minVolume: 150 },
  pfr_pass_pressure_pct: { volumeStats: PASS_ATTEMPT_VOLUME_STATS, minVolume: 150 },
};

/**
 * Returns true when a player qualifies for a stat's sample-size rule.
 * @param {{ stats?: Record<string, number> }} player
 * @param {string} stat
 */
export function meetsStatThreshold(player, stat) {
  const threshold = STAT_THRESHOLDS[stat];
  if (!threshold) return true;
  const volume = threshold.volumeStats
    .map((key) => player?.stats?.[key])
    .find((value) => typeof value === 'number');
  return typeof volume === 'number' && volume >= threshold.minVolume;
}
