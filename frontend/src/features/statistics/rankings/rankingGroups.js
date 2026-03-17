// Ranking-specific stat groups, separate from production display groups.

export const RANKING_GROUPS = {
  Overall: {
    'Positional Dominance': ['fp_ppr_rank', 'exp_fp_rank'],
    'Volume Dominance': ['pass_att_rank', 'rush_att_rank', 'targets_rank'],
    'Yardage Dominance': ['pass_yds_rank', 'rush_yds_rank', 'rec_yds_rank'],
    'Touchdown Dominance': ['pass_td_rank', 'rush_td_rank', 'rec_td_rank'],
  },
  QB: {
    'Passing Volume': ['pass_att', 'completions', 'pass_yds', 'pass_td'],
    'Passing Efficiency': ['passing_epa', 'passing_cpoe', 'pacr', 'ng_pass_passer_rating'],
    'Accuracy & Risk': ['pfr_pass_on_tgt_pct', 'pfr_pass_bad_throw_pct', 'passing_interceptions', 'pfr_pass_pressure_pct'],
    'Rushing Bonus': ['rush_att', 'rush_yds', 'rush_td'],
  },
  RB: {
    Workload: ['rush_att', 'target_share', 'sc_offense_pct'],
    'Rushing Production': ['rush_yds', 'rush_td', 'pfr_rush_yac', 'pfr_rush_brk_tkl'],
    'Rushing Efficiency': [
      'Yds/Rush',
      'rushing_epa',
      'ng_rush_rush_yds_over_exp_per_att',
      'ng_rush_efficiency',
      'pfr_rush_yac_att',
      'pfr_rush_ybc_att',
    ],
    'Receiving Impact': [
      'targets',
      'rec',
      'rec_yds',
      'rec_td',
      'receiving_yards_after_catch',
      'pfr_rec_brk_tkl',
      'Yds/Rec',
      'receiving_epa',
      'pfr_rec_yac_r',
      'pfr_rec_drop_pct',
    ],
  },
  WR: {
    Opportunity: ['targets', 'target_share', 'air_yards_share', 'wopr', 'sc_offense_pct'],
    'Receiving Production': ['rec', 'rec_yds', 'rec_td', 'receiving_yards_after_catch', 'pfr_rec_brk_tkl'],
    'Receiving Efficiency': ['Yds/Rec', 'receiving_epa', 'racr', 'pfr_rec_yac_r', 'pfr_rec_drop_pct'],
    'Route & Separation': [
      'ng_rec_avg_separation',
      'pfr_rec_adot',
      'ng_rec_catch_pct',
      'ng_rec_avg_yac',
      'ng_rec_avg_yac_above_expectation',
    ],
  },
  TE: {
    Opportunity: ['targets', 'target_share', 'air_yards_share', 'wopr', 'sc_offense_pct'],
    'Receiving Production': ['rec', 'rec_yds', 'rec_td', 'receiving_yards_after_catch', 'pfr_rec_brk_tkl'],
    'Receiving Efficiency': ['Yds/Rec', 'receiving_epa', 'racr', 'pfr_rec_yac_r', 'pfr_rec_drop_pct'],
    'Route & Separation': [
      'ng_rec_avg_separation',
      'pfr_rec_adot',
      'ng_rec_catch_pct',
      'ng_rec_avg_yac',
      'ng_rec_avg_yac_above_expectation',
    ],
  },
};
