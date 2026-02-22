/* Category configs for advanced player stat tabs. */

const SUMMARY_STATS = ['fp_ppr', 'fp_std', 'exp_fp'];
const USAGE_SHARE_STATS = ['target_share', 'air_yards_share', 'wopr', 'sc_offense_snaps', 'sc_offense_pct'];
const OPP_MODEL_ATTEMPT_STATS = ['ffo_pass_att', 'ffo_rush_att', 'ffo_rec_att'];

const CORE_EFFICIENCY_STATS = ['Yds/Rush', 'Yds/Rec', 'passing_epa', 'rushing_epa', 'receiving_epa', 'passing_cpoe', 'pacr', 'racr'];
const NEXTGEN_PASSING_STATS = [
  'ng_pass_passer_rating',
  'ng_pass_cmp_pct',
  'ng_pass_exp_cmp_pct',
  'ng_pass_cmp_pct_above_expectation',
  'ng_pass_aggressiveness',
  'ng_pass_avg_time_to_throw',
  'ng_pass_avg_air_yds_to_sticks',
];
const NEXTGEN_RECEIVING_STATS = [
  'ng_rec_catch_pct',
  'ng_rec_avg_separation',
  'ng_rec_avg_cushion',
  'ng_rec_avg_yac',
  'ng_rec_avg_exp_yac',
  'ng_rec_avg_yac_above_expectation',
  'ng_rec_pct_share_of_intended_air_yds',
];
const NEXTGEN_RUSHING_STATS = [
  'ng_rush_efficiency',
  'ng_rush_avg_rush_yds',
  'ng_rush_rush_yds_over_exp',
  'ng_rush_rush_yds_over_exp_per_att',
  'ng_rush_rush_pct_over_exp',
  'ng_rush_avg_time_to_los',
  'ng_rush_pct_att_gte_eight_defenders',
];
const PFR_DETAIL_STATS = [
  'pfr_pass_pressure_pct',
  'pfr_pass_drop_pct',
  'pfr_pass_bad_throw_pct',
  'pfr_pass_times_pressured',
  'pfr_rush_ybc_att',
  'pfr_rush_yac_att',
  'pfr_rush_brk_tkl',
  'pfr_rec_ybc_r',
  'pfr_rec_yac_r',
  'pfr_rec_drop_pct',
  'pfr_rec_brk_tkl',
];

const PERCENTILE_STATS = ['fp_ppr_pct', 'pass_att_pct', 'pass_yds_pct', 'rush_att_pct', 'rush_yds_pct', 'rec_yds_pct', 'targets_pct', 'exp_fp_pct'];
const OPP_MODEL_EXPECTED_STATS = ['ffo_total_fp_exp', 'ffo_total_yds_gained_exp', 'ffo_total_td_exp'];
const OPP_MODEL_REALIZED_STATS = ['ffo_total_fp', 'ffo_total_yds_gained', 'ffo_total_td'];
const OPP_MODEL_DELTA_STATS = ['ffo_total_fp_diff', 'ffo_total_yds_gained_diff', 'ffo_total_td_diff'];

export const OPPORTUNITY_CATEGORY_MAP = {
  'Share Signals': USAGE_SHARE_STATS,
  'Model Opportunity': [...OPP_MODEL_ATTEMPT_STATS, ...OPP_MODEL_EXPECTED_STATS],
  'Realized Outcome': OPP_MODEL_REALIZED_STATS,
};

export const EFFICIENCY_CATEGORY_MAP = {
  'Core Efficiency': CORE_EFFICIENCY_STATS,
  'Next Gen Passing': NEXTGEN_PASSING_STATS,
  'Next Gen Receiving': NEXTGEN_RECEIVING_STATS,
  'Next Gen Rushing': NEXTGEN_RUSHING_STATS,
  'PFR Detail': PFR_DETAIL_STATS,
};

export const INTERPRETATION_CATEGORY_MAP = {
  Composite: ['volume_score', ...SUMMARY_STATS],
  Percentiles: PERCENTILE_STATS,
  'Gap To Expectation': OPP_MODEL_DELTA_STATS,
};
