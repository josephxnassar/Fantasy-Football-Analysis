/* Canonical stat metadata and position group definitions. */

export const STAT_META = {
  // Fantasy summary + composite metrics.
  fp_ppr: {label: 'PPR Pts', description: 'PPR fantasy points.', format: 'decimal1'},
  fp_std: {label: 'Non-PPR Pts', description: 'Standard (non-PPR) fantasy points.', format: 'decimal1'},
  exp_fp: {label: 'Expected Pts', description: 'Expected fantasy points from opportunity model.', format: 'decimal1'},
  volume_score: {label: 'Volume Score', description: 'Blend of usage percentiles (pass/rush/target volume).', format: 'decimal1'},

  // Core box score passing stats.
  completions: { label: 'Comp', description: 'Completions.', format: 'int' },
  attempts: { label: 'Pass Att', description: 'Passing attempts.', format: 'int' },
  pass_att: { label: 'Pass Att', description: 'Passing attempts.', format: 'int' },
  pass_yds: { label: 'Pass Yds', description: 'Passing yards.', format: 'int' },
  pass_td: { label: 'Pass TD', description: 'Passing touchdowns.', format: 'int' },

  // Core box score rushing stats.
  carries: { label: 'Carries', description: 'Rushing attempts.', format: 'int' },
  rush_att: { label: 'Carries', description: 'Rushing attempts.', format: 'int' },
  rushing_yards: { label: 'Rush Yds', description: 'Rushing yards.', format: 'int' },
  rush_yds: { label: 'Rush Yds', description: 'Rushing yards.', format: 'int' },
  rushing_tds: { label: 'Rush TD', description: 'Rushing touchdowns.', format: 'int' },
  rush_td: { label: 'Rush TD', description: 'Rushing touchdowns.', format: 'int' },

  // Core box score receiving stats.
  receptions: { label: 'Rec', description: 'Receptions.', format: 'int' },
  receiving_yards: { label: 'Rec Yds', description: 'Receiving yards.', format: 'int' },
  receiving_tds: { label: 'Rec TD', description: 'Receiving touchdowns.', format: 'int' },
  rec: { label: 'Rec', description: 'Receptions.', format: 'int' },
  targets: { label: 'Tgt', description: 'Targets.', format: 'int' },
  rec_yds: { label: 'Rec Yds', description: 'Receiving yards.', format: 'int' },
  rec_td: { label: 'Rec TD', description: 'Receiving touchdowns.', format: 'int' },

  // Role/usage and snap-share stats.
  passing_first_downs: { label: 'Pass 1D', description: 'Passing first downs.', format: 'int' },
  rushing_first_downs: { label: 'Rush 1D', description: 'Rushing first downs.', format: 'int' },
  receiving_first_downs: { label: 'Rec 1D', description: 'Receiving first downs.', format: 'int' },
  target_share: { label: 'Target Share', description: 'Target share.', format: 'decimal2' },
  air_yards_share: { label: 'Air Yd Share', description: 'Air-yard share.', format: 'decimal2' },
  wopr: { label: 'WOPR', description: 'Weighted Opportunity Rating.', format: 'decimal2' },
  sc_offense_snaps: { label: 'Off Snaps', description: 'Offensive snaps played.', format: 'int' },
  sc_offense_pct: { label: 'Off Snap %', description: 'Offensive snap rate.', format: 'decimal1' },

  // Fantasy opportunity model outputs (ffo_*).
  ffo_pass_att: { label: 'FFO Pass Att', description: 'Model passing attempts.', format: 'decimal1' },
  ffo_rush_att: { label: 'FFO Rush Att', description: 'Model rushing attempts.', format: 'decimal1' },
  ffo_rec_att: { label: 'FFO Rec Att', description: 'Model receiving attempts.', format: 'decimal1' },
  ffo_total_fp: { label: 'FFO FP', description: 'Model fantasy points.', format: 'decimal1' },
  ffo_total_fp_exp: { label: 'FFO xFP', description: 'Expected fantasy points.', format: 'decimal1' },
  ffo_total_fp_diff: { label: 'FFO FP Delta', description: 'Actual minus expected fantasy points.', format: 'decimal1' },
  ffo_total_yds_gained: { label: 'FFO Yds', description: 'Model total yards gained.', format: 'decimal1' },
  ffo_total_yds_gained_exp: { label: 'FFO xYds', description: 'Expected total yards gained.', format: 'decimal1' },
  ffo_total_yds_gained_diff: { label: 'FFO Yds Delta', description: 'Actual minus expected total yards.', format: 'decimal1' },
  ffo_total_td: { label: 'FFO TD', description: 'Model touchdowns.', format: 'decimal1' },
  ffo_total_td_exp: { label: 'FFO xTD', description: 'Expected touchdowns.', format: 'decimal1' },
  ffo_total_td_diff: { label: 'FFO TD Delta', description: 'Actual minus expected touchdowns.', format: 'decimal1' },

  // Core efficiency calculations.
  passing_epa: { label: 'Pass EPA', description: 'Passing expected points added.', format: 'decimal2' },
  rushing_epa: { label: 'Rush EPA', description: 'Rushing expected points added.', format: 'decimal2' },
  receiving_epa: { label: 'Rec EPA', description: 'Receiving expected points added.', format: 'decimal2' },
  passing_cpoe: { label: 'Pass CPOE', description: 'Completion percentage over expectation.', format: 'decimal2' },
  pacr: { label: 'PACR', description: 'Passing air conversion ratio.', format: 'decimal2' },
  racr: { label: 'RACR', description: 'Receiving air conversion ratio.', format: 'decimal2' },

  // Next Gen passing profile.
  ng_pass_passer_rating: { label: 'NG Passer Rating', description: 'Next Gen passer rating.', format: 'decimal1' },
  ng_pass_cmp_pct: { label: 'NG Comp %', description: 'Next Gen completion rate.', format: 'decimal1' },
  ng_pass_exp_cmp_pct: { label: 'NG Exp Comp %', description: 'Next Gen expected completion rate.', format: 'decimal1' },
  ng_pass_cmp_pct_above_expectation: { label: 'NG CPOE', description: 'Next Gen completion rate above expectation.', format: 'decimal2' },
  ng_pass_aggressiveness: { label: 'NG Aggressiveness', description: 'Next Gen aggressiveness.', format: 'decimal1' },
  ng_pass_avg_time_to_throw: { label: 'NG Time To Throw', description: 'Average time to throw.', format: 'decimal2' },
  ng_pass_avg_air_yds_to_sticks: { label: 'NG Air Yds To Sticks', description: 'Air yards relative to sticks.', format: 'decimal2' },

  // Next Gen receiving profile.
  ng_rec_catch_pct: { label: 'NG Catch %', description: 'Next Gen catch rate.', format: 'decimal1' },
  ng_rec_avg_separation: { label: 'NG Separation', description: 'Average separation.', format: 'decimal2' },
  ng_rec_avg_cushion: { label: 'NG Cushion', description: 'Average cushion.', format: 'decimal2' },
  ng_rec_avg_yac: { label: 'NG YAC', description: 'Average YAC.', format: 'decimal2' },
  ng_rec_avg_exp_yac: { label: 'NG Exp YAC', description: 'Expected YAC.', format: 'decimal2' },
  ng_rec_avg_yac_above_expectation: { label: 'NG YAC Over Exp', description: 'YAC above expectation.', format: 'decimal2' },
  ng_rec_pct_share_of_intended_air_yds: { label: 'NG Air Share', description: 'Share of intended air yards.', format: 'decimal2' },

  // Next Gen rushing profile.
  ng_rush_efficiency: { label: 'NG Rush Efficiency', description: 'Next Gen rushing efficiency.', format: 'decimal2' },
  ng_rush_avg_rush_yds: { label: 'NG Yds/Carry', description: 'Average rushing yards per attempt.', format: 'decimal2' },
  ng_rush_rush_yds_over_exp: { label: 'NG Yds Over Exp', description: 'Rushing yards over expectation.', format: 'decimal1' },
  ng_rush_rush_yds_over_exp_per_att: { label: 'NG Yds Over Exp/Att', description: 'Rushing yards over expectation per attempt.', format: 'decimal2' },
  ng_rush_rush_pct_over_exp: { label: 'NG % Over Exp', description: 'Rushing percentage over expectation.', format: 'decimal2' },
  ng_rush_avg_time_to_los: { label: 'NG Time To LOS', description: 'Average time to line of scrimmage.', format: 'decimal2' },
  ng_rush_pct_att_gte_eight_defenders: { label: 'NG 8+ Box %', description: 'Rush attempts vs 8+ defenders.', format: 'decimal1' },

  // PFR advanced detail stats.
  pfr_pass_pressure_pct: { label: 'PFR Pressure %', description: 'Pressure rate from PFR.', format: 'decimal2' },
  pfr_pass_drop_pct: { label: 'PFR Drop %', description: 'Drop rate from PFR.', format: 'decimal2' },
  pfr_pass_bad_throw_pct: { label: 'PFR Bad Throw %', description: 'Bad throw rate from PFR.', format: 'decimal2' },
  pfr_pass_times_pressured: { label: 'PFR Pressures', description: 'Times pressured from PFR.', format: 'decimal1' },
  pfr_rush_ybc_att: { label: 'PFR YBC/Att', description: 'Yards before contact per carry.', format: 'decimal2' },
  pfr_rush_yac_att: { label: 'PFR YAC/Att', description: 'Yards after contact per carry.', format: 'decimal2' },
  pfr_rush_brk_tkl: { label: 'PFR Broken Tackles', description: 'Broken tackles on rushes.', format: 'decimal1' },
  pfr_rec_ybc_r: { label: 'PFR YBC/Rec', description: 'Yards before catch per reception.', format: 'decimal2' },
  pfr_rec_yac_r: { label: 'PFR YAC/Rec', description: 'Yards after catch per reception.', format: 'decimal2' },
  pfr_rec_drop_pct: { label: 'PFR Rec Drop %', description: 'Receiving drop rate.', format: 'decimal2' },
  pfr_rec_brk_tkl: { label: 'PFR Rec Broken Tackles', description: 'Broken tackles after reception.', format: 'decimal1' },

  // Derived interpretation percentiles.
  fp_ppr_pct: {label: 'PPR Percentile', description: 'Percentile rank in PPR points vs same position context.', format: 'percent1'},
  pass_att_pct: {label: 'Pass Att Percentile', description: 'Percentile rank in passing volume.', format: 'percent1'},
  pass_yds_pct: {label: 'Pass Yds Percentile', description: 'Percentile rank in passing yards.', format: 'percent1'},
  rush_att_pct: {label: 'Rush Att Percentile', description: 'Percentile rank in rushing volume.', format: 'percent1'},
  rush_yds_pct: {label: 'Rush Yds Percentile', description: 'Percentile rank in rushing yards.', format: 'percent1'},
  rec_yds_pct: {label: 'Rec Yds Percentile', description: 'Percentile rank in receiving yards.', format: 'percent1'},
  targets_pct: {label: 'Target Percentile', description: 'Percentile rank in targets.', format: 'percent1'},
  exp_fp_pct: {label: 'Expected Pts Percentile', description: 'Percentile rank in expected points.', format: 'percent1'},

  // Rate stats created in backend for convenience in UI.
  'Yds/Rec': {label: 'Yds/Rec', description: 'Yards per reception.', format: 'decimal1'},
  'Yds/Rush': {label: 'Yds/Rush', description: 'Yards per rush attempt.', format: 'decimal1'},
};

// Shared default stat buckets for position-based fantasy tab grouping.
const CORE_STATS = ['fp_ppr', 'fp_std', 'exp_fp'];
const PASSING_STATS = ['pass_att', 'pass_yds', 'pass_td'];
const RUSHING_STATS = ['rush_att', 'rush_yds', 'rush_td', 'Yds/Rush'];
const RECEIVING_STATS = ['targets', 'rec', 'rec_yds', 'rec_td', 'Yds/Rec'];

// Position-aware grouping map consumed by groupStatsByPosition.
export const POSITION_STAT_GROUPS = {
  Overall: {Core: CORE_STATS, Passing: PASSING_STATS, Rushing: RUSHING_STATS, Receiving: RECEIVING_STATS},
  QB: {Core: CORE_STATS, Passing: PASSING_STATS, Rushing: RUSHING_STATS},
  RB: {Core: CORE_STATS, Rushing: RUSHING_STATS, Receiving: RECEIVING_STATS},
  WR: {Core: CORE_STATS, Receiving: RECEIVING_STATS, Rushing: RUSHING_STATS},
  TE: {Core: CORE_STATS, Receiving: RECEIVING_STATS},
};
