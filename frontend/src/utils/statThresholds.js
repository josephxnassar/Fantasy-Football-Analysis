// Minimum thresholds used before color-scoring certain stats.

export const STAT_THRESHOLDS = {
  'Yds/Rush': { volumeStats: ['rush_att', 'carries'], minVolume: 100 },
  'Yds/Rec': { volumeStats: ['rec', 'receptions'], minVolume: 50 },
  ng_rush_efficiency: { volumeStats: ['rush_att'], minVolume: 100 },
  pfr_rush_yac_att: { volumeStats: ['rush_att'], minVolume: 100 },
  pfr_rush_ybc_att: { volumeStats: ['rush_att'], minVolume: 100 },
  receiving_epa: { volumeStats: ['targets'], minVolume: 50 },
  racr: { volumeStats: ['targets'], minVolume: 50 },
  pfr_rec_drop_pct: { volumeStats: ['targets'], minVolume: 50 },
  ng_rec_avg_separation: { volumeStats: ['targets'], minVolume: 50 },
  pfr_rec_adot: { volumeStats: ['targets'], minVolume: 50 },
  ng_rec_catch_pct: { volumeStats: ['targets'], minVolume: 50 },
  ng_rec_avg_yac: { volumeStats: ['rec'], minVolume: 40 },
  ng_rec_avg_yac_above_expectation: { volumeStats: ['rec'], minVolume: 40 },
  pfr_rec_yac_r: { volumeStats: ['rec'], minVolume: 40 },
  passing_cpoe: { volumeStats: ['pass_att'], minVolume: 150 },
  pacr: { volumeStats: ['pass_att'], minVolume: 150 },
  ng_pass_passer_rating: { volumeStats: ['pass_att'], minVolume: 150 },
  ng_pass_avg_time_to_throw: { volumeStats: ['pass_att'], minVolume: 150 },
  pfr_pass_bad_throw_pct: { volumeStats: ['pass_att'], minVolume: 150 },
  pfr_pass_on_tgt_pct: { volumeStats: ['pass_att'], minVolume: 150 },
  pfr_pass_pressure_pct: { volumeStats: ['pass_att'], minVolume: 150 },
};

export function meetsStatThreshold(player, stat) {
  const threshold = STAT_THRESHOLDS[stat];
  if (!threshold) return true;
  const volume = threshold.volumeStats
    .map((key) => player?.stats?.[key])
    .find((value) => typeof value === 'number');
  return typeof volume === 'number' && volume >= threshold.minVolume;
}
