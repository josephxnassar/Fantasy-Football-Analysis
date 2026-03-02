/* Canonical stat metadata and position group definitions. */

export const STAT_META = {
  // Fantasy summary.
  fp_ppr: {label: 'PPR Pts', description: 'Total fantasy points in PPR scoring, where each reception adds 1 point on top of standard scoring.', format: 'decimal1'},
  fp_std: {label: 'Non-PPR Pts', description: 'Total fantasy points in standard scoring — touchdowns, yards, and turnovers only, no bonus for catches.', format: 'decimal1'},
  exp_fp: {label: 'Expected Pts', description: 'How many fantasy points a player "should" have scored based on their opportunities. Higher than actual = unlucky; lower = efficient.', format: 'decimal1'},

  // Passing.
  attempts: { label: 'Pass Att', description: 'Total passing attempts.', format: 'int' },
  pass_att: { label: 'Pass Att', description: 'Total passing attempts.', format: 'int' },
  pass_yds: { label: 'Pass Yds', description: 'Total passing yards through the air.', format: 'int' },
  pass_td: { label: 'Pass TD', description: 'Passing touchdowns thrown.', format: 'int' },

  // Rushing.
  carries: { label: 'Carries', description: 'Total rushing attempts.', format: 'int' },
  rush_att: { label: 'Carries', description: 'Total rushing attempts.', format: 'int' },
  rushing_yards: { label: 'Rush Yds', description: 'Total rushing yards.', format: 'int' },
  rush_yds: { label: 'Rush Yds', description: 'Total rushing yards.', format: 'int' },
  rushing_tds: { label: 'Rush TD', description: 'Rushing touchdowns scored.', format: 'int' },
  rush_td: { label: 'Rush TD', description: 'Rushing touchdowns scored.', format: 'int' },

  // Receiving.
  receptions: { label: 'Rec', description: 'Total catches. Worth 1 point each in PPR formats.', format: 'int' },
  receiving_yards: { label: 'Rec Yds', description: 'Total receiving yards.', format: 'int' },
  receiving_tds: { label: 'Rec TD', description: 'Receiving touchdowns scored.', format: 'int' },
  rec: { label: 'Rec', description: 'Total catches. Worth 1 point each in PPR formats.', format: 'int' },
  targets: { label: 'Tgt', description: 'Times a pass was thrown to this player — a key indicator of offensive involvement.', format: 'int' },
  rec_yds: { label: 'Rec Yds', description: 'Total receiving yards.', format: 'int' },
  rec_td: { label: 'Rec TD', description: 'Receiving touchdowns scored.', format: 'int' },

  // Usage.
  target_share: { label: 'Target Share', description: 'Percentage of the team\'s pass targets going to this player. 20%+ is elite for WRs.', format: 'decimal2' },
  wopr: { label: 'WOPR', description: 'Weighted Opportunity Rating — combines target share and air yard share into a single receiving usage score.', format: 'decimal2' },

  // Percentile ranks (within same position + season).
  fp_ppr_pct: { label: 'PPR Pts %ile', description: 'Percentile rank for PPR fantasy points among the same position. 90+ = elite tier.', format: 'decimal1' },
  pass_att_pct: { label: 'Pass Att %ile', description: 'Percentile rank for passing attempts among QBs — measures volume relative to peers.', format: 'decimal1' },
  pass_yds_pct: { label: 'Pass Yds %ile', description: 'Percentile rank for passing yards among QBs.', format: 'decimal1' },
  rush_att_pct: { label: 'Carries %ile', description: 'Percentile rank for rushing attempts — shows workload relative to position peers.', format: 'decimal1' },
  rush_yds_pct: { label: 'Rush Yds %ile', description: 'Percentile rank for rushing yards among same position.', format: 'decimal1' },
  targets_pct: { label: 'Targets %ile', description: 'Percentile rank for targets — shows how heavily targeted vs. same position.', format: 'decimal1' },
  rec_yds_pct: { label: 'Rec Yds %ile', description: 'Percentile rank for receiving yards among same position.', format: 'decimal1' },
  exp_fp_pct: { label: 'Exp Pts %ile', description: 'Percentile rank for expected fantasy points — compares opportunity quality vs. peers.', format: 'decimal1' },

  // Efficiency.
  passing_epa: { label: 'Pass EPA', description: 'Expected Points Added per pass attempt. Positive is good.', format: 'decimal2' },
  rushing_epa: { label: 'Rush EPA', description: 'Expected Points Added per carry. Positive is good.', format: 'decimal2' },
  receiving_epa: { label: 'Rec EPA', description: 'Expected Points Added per target. Positive is good.', format: 'decimal2' },
  passing_cpoe: { label: 'CPOE', description: 'Completion Percentage Over Expectation — how much better or worse than expected given throw difficulty.', format: 'decimal2' },
  pacr: { label: 'PACR', description: 'Passing Air Conversion Ratio — passing yards ÷ intended air yards. Above 1.0 = YAC boosting production.', format: 'decimal2' },
  racr: { label: 'RACR', description: 'Receiving Air Conversion Ratio — receiving yards ÷ air yards targeted. Above 1.0 = strong YAC.', format: 'decimal2' },
  'Yds/Rec': {label: 'Yds/Rec', description: 'Yards per reception. Higher indicates big-play ability or deeper routes.', format: 'decimal1'},
  'Yds/Rush': {label: 'Yds/Rush', description: 'Yards per carry. League average is ~4.3; elite backs hit 5.0+.', format: 'decimal1'},

  // Next Gen highlights.
  ng_pass_passer_rating: { label: 'Passer Rating', description: 'NFL passer rating (0–158.3). League average is around 90.', format: 'decimal1' },
  ng_pass_avg_time_to_throw: { label: 'Time To Throw', description: 'Average seconds from snap to throw. Quick (<2.5s) = short game; slow (>3.0s) = deep shots or pressure.', format: 'decimal2' },
  ng_rec_avg_separation: { label: 'Separation', description: 'Average yards of separation from the nearest defender at the throw. More = easier catches.', format: 'decimal2' },
  ng_rec_avg_yac_above_expectation: { label: 'YAC Over Exp', description: 'Actual minus expected yards after catch. Positive = creating extra yards beyond what the catch location would predict.', format: 'decimal2' },
  ng_rec_catch_pct: { label: 'Catch %', description: 'Percentage of targets caught.', format: 'decimal1' },
  ng_rush_rush_yds_over_exp_per_att: { label: 'RYOE/Att', description: 'Rushing yards over expectation per carry. The best per-play measure of rushing talent — removes O-line effects.', format: 'decimal2' },
  ng_rush_efficiency: { label: 'Rush Efficiency', description: 'Yards gained ÷ yards expected from blocking/alignment. Above 100% = beating blocks.', format: 'decimal2' },

  // PFR highlights.
  pfr_pass_pressure_pct: { label: 'Pressure %', description: 'Percentage of dropbacks where the QB was pressured. Lower = better protection or quicker release.', format: 'decimal2' },
  pfr_pass_bad_throw_pct: { label: 'Bad Throw %', description: 'Percentage of passes charted as uncatchable. Directly measures accuracy issues.', format: 'decimal2' },
  pfr_rush_yac_att: { label: 'YAC/Att', description: 'Yards After Contact per carry — measures a back\'s power and elusiveness independent of blocking.', format: 'decimal2' },
  pfr_rush_brk_tkl: { label: 'Broken Tackles', description: 'Total broken tackles on rushing plays. Indicates physicality.', format: 'decimal1' },
  pfr_rec_drop_pct: { label: 'Drop %', description: 'Percentage of catchable targets dropped. Lower = more reliable hands.', format: 'decimal2' },
  pfr_rec_yac_r: { label: 'YAC/Rec', description: 'Yards After Catch per reception — measures ability to create with the ball in hand.', format: 'decimal2' },
};

// ── Production tab: core fantasy box-score stats per position ──
export const PRODUCTION_GROUPS = {
  QB: {
    Fantasy: ['fp_ppr', 'fp_std', 'exp_fp'],
    Passing: ['pass_att', 'pass_yds', 'pass_td'],
    Rushing: ['rush_att', 'rush_yds', 'rush_td'],
    Percentiles: ['fp_ppr_pct', 'exp_fp_pct', 'pass_att_pct', 'pass_yds_pct', 'rush_att_pct', 'rush_yds_pct'],
  },
  RB: {
    Fantasy: ['fp_ppr', 'fp_std', 'exp_fp'],
    Rushing: ['rush_att', 'rush_yds', 'rush_td'],
    Receiving: ['targets', 'rec', 'rec_yds', 'rec_td'],
    Usage: ['target_share', 'wopr'],
    Percentiles: ['fp_ppr_pct', 'exp_fp_pct', 'rush_att_pct', 'rush_yds_pct', 'targets_pct', 'rec_yds_pct'],
  },
  WR: {
    Fantasy: ['fp_ppr', 'fp_std', 'exp_fp'],
    Receiving: ['targets', 'rec', 'rec_yds', 'rec_td'],
    Usage: ['target_share', 'wopr'],
    Percentiles: ['fp_ppr_pct', 'exp_fp_pct', 'targets_pct', 'rec_yds_pct'],
  },
  TE: {
    Fantasy: ['fp_ppr', 'fp_std', 'exp_fp'],
    Receiving: ['targets', 'rec', 'rec_yds', 'rec_td'],
    Usage: ['target_share', 'wopr'],
    Percentiles: ['fp_ppr_pct', 'exp_fp_pct', 'targets_pct', 'rec_yds_pct'],
  },
  Overall: {
    Fantasy: ['fp_ppr', 'fp_std', 'exp_fp'],
    Passing: ['pass_att', 'pass_yds', 'pass_td'],
    Rushing: ['rush_att', 'rush_yds', 'rush_td'],
    Receiving: ['targets', 'rec', 'rec_yds', 'rec_td'],
    Percentiles: ['fp_ppr_pct', 'exp_fp_pct'],
  },
};

// ── Advanced tab: best efficiency + tracking metrics per position ──
export const ADVANCED_GROUPS = {
  QB: {
    Efficiency: ['passing_epa', 'passing_cpoe', 'pacr'],
    'Next Gen': ['ng_pass_passer_rating', 'ng_pass_avg_time_to_throw'],
    PFR: ['pfr_pass_pressure_pct', 'pfr_pass_bad_throw_pct'],
  },
  RB: {
    Efficiency: ['Yds/Rush', 'rushing_epa'],
    'Next Gen': ['ng_rush_rush_yds_over_exp_per_att', 'ng_rush_efficiency'],
    PFR: ['pfr_rush_yac_att', 'pfr_rush_brk_tkl'],
  },
  WR: {
    Efficiency: ['Yds/Rec', 'receiving_epa', 'racr'],
    'Next Gen': ['ng_rec_avg_separation', 'ng_rec_avg_yac_above_expectation', 'ng_rec_catch_pct'],
    PFR: ['pfr_rec_drop_pct', 'pfr_rec_yac_r'],
  },
  TE: {
    Efficiency: ['Yds/Rec', 'receiving_epa', 'racr'],
    'Next Gen': ['ng_rec_avg_separation', 'ng_rec_avg_yac_above_expectation', 'ng_rec_catch_pct'],
    PFR: ['pfr_rec_drop_pct', 'pfr_rec_yac_r'],
  },
  Overall: {
    Efficiency: ['passing_epa', 'rushing_epa', 'receiving_epa', 'Yds/Rush', 'Yds/Rec'],
  },
};
