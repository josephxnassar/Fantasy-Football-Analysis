/* Canonical stat metadata and position group definitions. */

export const STAT_META = {
  // Fantasy summary.
  fp_ppr: {label: 'PPR Pts', description: 'Total fantasy points in PPR scoring, where each reception adds 1 point on top of standard scoring.', format: 'decimal1'},
  fp_std: {label: 'Non-PPR Pts', description: 'Total fantasy points in standard scoring — touchdowns, yards, and turnovers only, no bonus for catches.', format: 'decimal1'},
  exp_fp: {label: 'Expected Pts', description: 'How many fantasy points a player "should" have scored based on their opportunities. Higher than actual = unlucky; lower = efficient.', format: 'decimal1'},

  // Passing.
  completions: { label: 'Comp', description: 'Completed passes.', format: 'int' },
  pass_att: { label: 'Pass Att', description: 'Total passing attempts.', format: 'int' },
  pass_yds: { label: 'Pass Yds', description: 'Total passing yards through the air.', format: 'int' },
  pass_td: { label: 'Pass TD', description: 'Passing touchdowns thrown.', format: 'int' },
  passing_interceptions: { label: 'INT', description: 'Interceptions thrown. Each costs roughly 2 fantasy points in standard scoring.', format: 'int' },

  // Rushing.
  rush_att: { label: 'Carries', description: 'Total rushing attempts.', format: 'int' },
  rush_yds: { label: 'Rush Yds', description: 'Total rushing yards.', format: 'int' },
  rush_td: { label: 'Rush TD', description: 'Rushing touchdowns scored.', format: 'int' },

  // Receiving.
  rec: { label: 'Rec', description: 'Total catches. Worth 1 point each in PPR formats.', format: 'int' },
  targets: { label: 'Tgt', description: 'Times a pass was thrown to this player — a key indicator of offensive involvement.', format: 'int' },
  rec_yds: { label: 'Rec Yds', description: 'Total receiving yards.', format: 'int' },
  rec_td: { label: 'Rec TD', description: 'Receiving touchdowns scored.', format: 'int' },
  receiving_yards_after_catch: { label: 'Rec YAC', description: 'Total receiving yards gained after the catch — shows how much a player creates with the ball in hand.', format: 'int' },

  // Usage.
  target_share: { label: 'Target Share', description: 'Percentage of the team\'s pass targets going to this player. 20%+ is elite for WRs.', format: 'decimal2' },
  air_yards_share: { label: 'Air Yard Share', description: 'Percentage of team air yards targeted to this player. High share signals a key role in the pass game.', format: 'decimal2' },
  wopr: { label: 'WOPR', description: 'Weighted Opportunity Rating — combines target share and air yard share into a single receiving usage score.', format: 'decimal2' },
  sc_offense_pct: { label: 'Snap %', description: 'Percentage of offensive snaps played. 80%+ indicates a true every-down role.', format: 'percent1' },

  // Position ranks (within same position + season, 1 = best).
  fp_ppr_rank: { label: 'PPR Pts Rank', description: 'Position rank for PPR fantasy points among the same position. 1 = best at the position.', format: 'int' },
  pass_att_rank: { label: 'Pass Att Rank', description: 'Position rank for passing attempts among QBs — measures volume relative to peers.', format: 'int' },
  pass_yds_rank: { label: 'Pass Yds Rank', description: 'Position rank for passing yards among QBs.', format: 'int' },
  pass_td_rank: { label: 'Pass TD Rank', description: 'Position rank for passing touchdowns among QBs.', format: 'int' },
  rush_att_rank: { label: 'Carries Rank', description: 'Position rank for rushing attempts — shows workload relative to position peers.', format: 'int' },
  rush_yds_rank: { label: 'Rush Yds Rank', description: 'Position rank for rushing yards among same position.', format: 'int' },
  rush_td_rank: { label: 'Rush TD Rank', description: 'Position rank for rushing touchdowns among same position.', format: 'int' },
  targets_rank: { label: 'Targets Rank', description: 'Position rank for targets — shows how heavily targeted vs. same position.', format: 'int' },
  rec_yds_rank: { label: 'Rec Yds Rank', description: 'Position rank for receiving yards among same position.', format: 'int' },
  rec_td_rank: { label: 'Rec TD Rank', description: 'Position rank for receiving touchdowns among same position.', format: 'int' },
  exp_fp_rank: { label: 'Exp Pts Rank', description: 'Position rank for expected fantasy points — compares opportunity quality vs. peers.', format: 'int' },

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
  ng_rec_avg_yac: { label: 'Avg YAC', description: 'Average yards after catch per reception from Next Gen tracking. Pure YAC ability measure.', format: 'decimal1' },
  ng_rec_avg_yac_above_expectation: { label: 'YAC Over Exp', description: 'Actual minus expected yards after catch. Positive = creating extra yards beyond what the catch location would predict.', format: 'decimal2' },
  ng_rec_catch_pct: { label: 'Catch %', description: 'Percentage of targets caught.', format: 'decimal1' },
  ng_rush_rush_yds_over_exp_per_att: { label: 'RYOE/Att', description: 'Rushing yards over expectation per carry. The best per-play measure of rushing talent — removes O-line effects.', format: 'decimal2' },
  ng_rush_efficiency: { label: 'Rush Efficiency', description: 'Yards gained ÷ yards expected from blocking/alignment. Above 100% = beating blocks.', format: 'decimal2' },

  // PFR highlights.
  pfr_pass_pressure_pct: { label: 'Pressure %', description: 'Percentage of dropbacks where the QB was pressured. Lower = better protection or quicker release.', format: 'decimal2' },
  pfr_pass_bad_throw_pct: { label: 'Bad Throw %', description: 'Percentage of passes charted as uncatchable. Directly measures accuracy issues.', format: 'decimal2' },
  pfr_pass_on_tgt_pct: { label: 'On-Target %', description: 'Percentage of passes rated on-target by PFR charting. Pure accuracy measure separate from completion %.', format: 'decimal1' },
  pfr_rush_yac_att: { label: 'YAC/Att', description: 'Yards After Contact per carry — measures a back\'s power and elusiveness independent of blocking.', format: 'decimal2' },
  pfr_rush_yac: { label: 'Rush YAC', description: 'Total rushing yards gained after contact with a defender. Raw volume measure of a runner\'s power.', format: 'int' },
  pfr_rush_ybc_att: { label: 'YBC/Att', description: 'Yards Before Contact per carry — measures blocking and scheme effectiveness before the runner makes a play.', format: 'decimal2' },
  pfr_rush_brk_tkl: { label: 'Broken Tackles', description: 'Total broken tackles on rushing plays. Indicates physicality.', format: 'decimal1' },
  pfr_rec_adot: { label: 'ADOT', description: 'Average Depth of Target — how far downfield this player is targeted on average.', format: 'decimal1' },
  pfr_rec_drop_pct: { label: 'Drop %', description: 'Percentage of catchable targets dropped. Lower = more reliable hands.', format: 'decimal2' },
  pfr_rec_yac_r: { label: 'YAC/Rec', description: 'Yards After Catch per reception — measures ability to create with the ball in hand.', format: 'decimal2' },
  pfr_rec_yac: { label: 'Rec YAC', description: 'Total receiving yards gained after the catch from PFR charting.', format: 'int' },
  pfr_rec_brk_tkl: { label: 'Broken Tackles', description: 'Receiving broken tackles — tacklers evaded after the catch.', format: 'int' },
};

// ── Production tab: all important fantasy stats grouped by topic ──
export const PRODUCTION_GROUPS = {
  QB: {
    Fantasy: ['fp_ppr', 'fp_std', 'exp_fp'],
    Passing: ['completions', 'pass_att', 'pass_yds', 'pass_td', 'passing_interceptions'],
    'Passing Efficiency': ['passing_epa', 'passing_cpoe', 'ng_pass_passer_rating', 'pacr'],
    'Accuracy & Pressure': ['pfr_pass_bad_throw_pct', 'pfr_pass_on_tgt_pct', 'pfr_pass_pressure_pct', 'ng_pass_avg_time_to_throw'],
    Rushing: ['rush_att', 'rush_yds', 'rush_td'],
    Rankings: ['fp_ppr_rank', 'exp_fp_rank', 'pass_att_rank', 'pass_yds_rank', 'pass_td_rank', 'rush_att_rank', 'rush_yds_rank', 'rush_td_rank'],
  },
  RB: {
    Fantasy: ['fp_ppr', 'fp_std', 'exp_fp'],
    Rushing: ['rush_att', 'rush_yds', 'rush_td', 'pfr_rush_yac', 'pfr_rush_brk_tkl'],
    'Rushing Efficiency': ['Yds/Rush', 'rushing_epa', 'ng_rush_rush_yds_over_exp_per_att', 'ng_rush_efficiency', 'pfr_rush_yac_att', 'pfr_rush_ybc_att'],
    Receiving: ['targets', 'rec', 'rec_yds', 'rec_td', 'receiving_yards_after_catch', 'pfr_rec_brk_tkl'],
    'Receiving Efficiency': ['Yds/Rec', 'receiving_epa', 'pfr_rec_drop_pct', 'pfr_rec_yac_r'],
    Usage: ['target_share', 'wopr', 'sc_offense_pct'],
    Rankings: ['fp_ppr_rank', 'exp_fp_rank', 'rush_att_rank', 'rush_yds_rank', 'rush_td_rank', 'targets_rank', 'rec_yds_rank', 'rec_td_rank'],
  },
  WR: {
    Fantasy: ['fp_ppr', 'fp_std', 'exp_fp'],
    Receiving: ['targets', 'rec', 'rec_yds', 'rec_td', 'receiving_yards_after_catch', 'pfr_rec_brk_tkl', 'ng_rec_avg_separation', 'pfr_rec_adot', 'ng_rec_catch_pct'],
    'Receiving Efficiency': ['Yds/Rec', 'receiving_epa', 'racr', 'pfr_rec_drop_pct', 'ng_rec_avg_yac', 'ng_rec_avg_yac_above_expectation', 'pfr_rec_yac_r'],
    Rushing: ['rush_att', 'rush_yds', 'rush_td', 'pfr_rush_brk_tkl'],
    'Rushing Efficiency': ['Yds/Rush', 'rushing_epa', 'ng_rush_rush_yds_over_exp_per_att', 'ng_rush_efficiency'],
    Usage: ['target_share', 'air_yards_share', 'wopr', 'sc_offense_pct'],
    Rankings: ['fp_ppr_rank', 'exp_fp_rank', 'targets_rank', 'rec_yds_rank', 'rec_td_rank'],
  },
  TE: {
    Fantasy: ['fp_ppr', 'fp_std', 'exp_fp'],
    Receiving: ['targets', 'rec', 'rec_yds', 'rec_td', 'receiving_yards_after_catch', 'pfr_rec_brk_tkl', 'ng_rec_avg_separation', 'pfr_rec_adot', 'ng_rec_catch_pct'],
    'Receiving Efficiency': ['Yds/Rec', 'receiving_epa', 'racr', 'pfr_rec_drop_pct', 'ng_rec_avg_yac', 'ng_rec_avg_yac_above_expectation', 'pfr_rec_yac_r'],
    Rushing: ['rush_att', 'rush_yds', 'rush_td', 'pfr_rush_brk_tkl'],
    'Rushing Efficiency': ['Yds/Rush', 'rushing_epa', 'ng_rush_rush_yds_over_exp_per_att', 'ng_rush_efficiency'],
    Usage: ['target_share', 'air_yards_share', 'wopr', 'sc_offense_pct'],
    Rankings: ['fp_ppr_rank', 'exp_fp_rank', 'targets_rank', 'rec_yds_rank', 'rec_td_rank'],
  },
  Overall: {
    Fantasy: ['fp_ppr', 'fp_std', 'exp_fp'],
    Passing: ['completions', 'pass_att', 'pass_yds', 'pass_td', 'passing_interceptions'],
    Rushing: ['rush_att', 'rush_yds', 'rush_td'],
    Receiving: ['targets', 'rec', 'rec_yds', 'rec_td'],
    Rankings: ['fp_ppr_rank', 'exp_fp_rank', 'pass_td_rank', 'rush_td_rank', 'rec_td_rank'],
  },
};
