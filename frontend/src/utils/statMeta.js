/* Canonical stat metadata and position group definitions. */

export const STAT_META = {
  // Fantasy summary + composite metrics.
  fp_ppr: {label: 'PPR Pts', description: 'Total fantasy points in PPR scoring, where each reception adds 1 point on top of standard scoring.', format: 'decimal1'},
  fp_std: {label: 'Non-PPR Pts', description: 'Total fantasy points in standard scoring — touchdowns, yards, and turnovers only, no bonus for catches.', format: 'decimal1'},
  exp_fp: {label: 'Expected Pts', description: 'How many fantasy points a player "should" have scored based on their opportunities (targets, carries, routes). Higher than actual = unlucky; lower = efficient.', format: 'decimal1'},
  volume_score: {label: 'Volume Score', description: 'A 0–100 composite blending passing, rushing, and target volume percentiles. Measures raw workload regardless of efficiency — higher means more involved.', format: 'decimal1'},

  // Core box score passing stats.
  completions: { label: 'Comp', description: 'Total completed passes.', format: 'int' },
  attempts: { label: 'Pass Att', description: 'Total passing attempts, including incomplete passes and interceptions.', format: 'int' },
  pass_att: { label: 'Pass Att', description: 'Total passing attempts, including incomplete passes and interceptions.', format: 'int' },
  pass_yds: { label: 'Pass Yds', description: 'Total passing yards through the air (includes yards after catch by receivers).', format: 'int' },
  pass_td: { label: 'Pass TD', description: 'Passing touchdowns thrown.', format: 'int' },

  // Core box score rushing stats.
  carries: { label: 'Carries', description: 'Total rushing attempts (handoffs, designed runs, scrambles).', format: 'int' },
  rush_att: { label: 'Carries', description: 'Total rushing attempts (handoffs, designed runs, scrambles).', format: 'int' },
  rushing_yards: { label: 'Rush Yds', description: 'Total rushing yards gained on the ground.', format: 'int' },
  rush_yds: { label: 'Rush Yds', description: 'Total rushing yards gained on the ground.', format: 'int' },
  rushing_tds: { label: 'Rush TD', description: 'Rushing touchdowns scored.', format: 'int' },
  rush_td: { label: 'Rush TD', description: 'Rushing touchdowns scored.', format: 'int' },

  // Core box score receiving stats.
  receptions: { label: 'Rec', description: 'Total catches. Worth 1 point each in PPR formats.', format: 'int' },
  receiving_yards: { label: 'Rec Yds', description: 'Total receiving yards after the catch is made.', format: 'int' },
  receiving_tds: { label: 'Rec TD', description: 'Receiving touchdowns scored.', format: 'int' },
  rec: { label: 'Rec', description: 'Total catches. Worth 1 point each in PPR formats.', format: 'int' },
  targets: { label: 'Tgt', description: 'Times a pass was thrown to this player, whether caught or not. A key indicator of offensive involvement.', format: 'int' },
  rec_yds: { label: 'Rec Yds', description: 'Total receiving yards after the catch is made.', format: 'int' },
  rec_td: { label: 'Rec TD', description: 'Receiving touchdowns scored.', format: 'int' },

  // Role/usage and snap-share stats.
  passing_first_downs: { label: 'Pass 1D', description: 'First downs gained through passing plays. Indicates drive-sustaining ability.', format: 'int' },
  rushing_first_downs: { label: 'Rush 1D', description: 'First downs gained on rushing plays. Signals a back who moves the chains.', format: 'int' },
  receiving_first_downs: { label: 'Rec 1D', description: 'First downs gained on receptions. Shows a receiver who converts on key downs.', format: 'int' },
  target_share: { label: 'Target Share', description: 'Percentage of the team\'s total pass targets that went to this player. 20%+ is elite for WRs.', format: 'decimal2' },
  air_yards_share: { label: 'Air Yd Share', description: 'Percentage of the team\'s total intended air yards directed at this player. Measures downfield usage, not just volume.', format: 'decimal2' },
  wopr: { label: 'WOPR', description: 'Weighted Opportunity Rating — combines target share (1.5×) and air yard share (0.7×) into a single receiving usage score. Higher = bigger passing-game role.', format: 'decimal2' },
  sc_offense_snaps: { label: 'Off Snaps', description: 'Number of offensive plays this player was on the field for. More snaps = more chances to produce.', format: 'int' },
  sc_offense_pct: { label: 'Off Snap %', description: 'Percentage of the team\'s offensive snaps this player played. 80%+ indicates a true starter workload.', format: 'decimal1' },

  // Fantasy opportunity model outputs (ffo_*).
  ffo_pass_att: { label: 'FFO Pass Att', description: 'Modeled passing attempts based on game script, matchup, and usage patterns.', format: 'decimal1' },
  ffo_rush_att: { label: 'FFO Rush Att', description: 'Modeled rushing attempts based on game script, matchup, and usage patterns.', format: 'decimal1' },
  ffo_rec_att: { label: 'FFO Rec Att', description: 'Modeled receiving opportunities based on route participation and target trends.', format: 'decimal1' },
  ffo_total_fp: { label: 'FFO FP', description: 'Total fantasy points produced from the opportunity model\'s tracked plays.', format: 'decimal1' },
  ffo_total_fp_exp: { label: 'FFO xFP', description: 'Expected fantasy points based purely on opportunity quality — removes luck and efficiency, isolating workload value.', format: 'decimal1' },
  ffo_total_fp_diff: { label: 'FFO FP Delta', description: 'Actual minus expected fantasy points. Positive = outperforming opportunities; negative = underperforming or unlucky.', format: 'decimal1' },
  ffo_total_yds_gained: { label: 'FFO Yds', description: 'Total yards gained from opportunity-model tracked plays.', format: 'decimal1' },
  ffo_total_yds_gained_exp: { label: 'FFO xYds', description: 'Expected total yards based on opportunity quality alone.', format: 'decimal1' },
  ffo_total_yds_gained_diff: { label: 'FFO Yds Delta', description: 'Actual minus expected yards. Positive = gaining more than expected from opportunities.', format: 'decimal1' },
  ffo_total_td: { label: 'FFO TD', description: 'Total touchdowns from opportunity-model tracked plays.', format: 'decimal1' },
  ffo_total_td_exp: { label: 'FFO xTD', description: 'Expected touchdowns from opportunity quality. TD scoring has high variance — compare over multiple weeks.', format: 'decimal1' },
  ffo_total_td_diff: { label: 'FFO TD Delta', description: 'Actual minus expected touchdowns. Positive = scoring more TDs than opportunity would predict.', format: 'decimal1' },

  // Core efficiency calculations.
  passing_epa: { label: 'Pass EPA', description: 'Expected Points Added on passing plays — how much each pass attempt improved or hurt scoring chances. Positive is good.', format: 'decimal2' },
  rushing_epa: { label: 'Rush EPA', description: 'Expected Points Added on rushing plays — how much each carry improved or hurt scoring chances. Positive is good.', format: 'decimal2' },
  receiving_epa: { label: 'Rec EPA', description: 'Expected Points Added on receiving plays — how much each target improved scoring chances. Positive is good.', format: 'decimal2' },
  passing_cpoe: { label: 'Pass CPOE', description: 'Completion Percentage Over Expectation — how much better (or worse) the QB completes passes compared to what\'s expected given throw difficulty.', format: 'decimal2' },
  pacr: { label: 'PACR', description: 'Passing Air Conversion Ratio — passing yards divided by intended air yards. Above 1.0 means YAC is boosting production; below 1.0 means deep throws aren\'t connecting.', format: 'decimal2' },
  racr: { label: 'RACR', description: 'Receiving Air Conversion Ratio — receiving yards divided by air yards targeted. Above 1.0 means strong YAC; below 1.0 means catches short of the target depth.', format: 'decimal2' },

  // Next Gen passing profile.
  ng_pass_passer_rating: { label: 'NG Passer Rating', description: 'NFL passer rating from Next Gen Stats tracking. Scale of 0–158.3; league average is around 90.', format: 'decimal1' },
  ng_pass_cmp_pct: { label: 'NG Comp %', description: 'Completion percentage from Next Gen tracking data.', format: 'decimal1' },
  ng_pass_exp_cmp_pct: { label: 'NG Exp Comp %', description: 'Expected completion percentage based on throw difficulty, separation, and distance. Compare to actual to gauge accuracy.', format: 'decimal1' },
  ng_pass_cmp_pct_above_expectation: { label: 'NG CPOE', description: 'Actual minus expected completion %. Positive = completing tougher throws; negative = missing easier ones.', format: 'decimal2' },
  ng_pass_aggressiveness: { label: 'NG Aggressiveness', description: 'Percentage of throws into tight coverage windows. Higher = more aggressive, but not necessarily better.', format: 'decimal1' },
  ng_pass_avg_time_to_throw: { label: 'NG Time To Throw', description: 'Average seconds from snap to throw. Quick (<2.5s) favors short passing; slow (>3.0s) suggests deep shots or pressure issues.', format: 'decimal2' },
  ng_pass_avg_air_yds_to_sticks: { label: 'NG Air Yds To Sticks', description: 'Average air yards relative to the first-down marker. Negative = throwing short of the sticks; positive = past them.', format: 'decimal2' },

  // Next Gen receiving profile.
  ng_rec_catch_pct: { label: 'NG Catch %', description: 'Percentage of targets caught. Depends on target quality — contested catches lower this.', format: 'decimal1' },
  ng_rec_avg_separation: { label: 'NG Separation', description: 'Average yards of separation from the nearest defender at the time of the throw. More separation = easier catches.', format: 'decimal2' },
  ng_rec_avg_cushion: { label: 'NG Cushion', description: 'Average yards between the receiver and cornerback at the snap. More cushion = softer coverage alignment.', format: 'decimal2' },
  ng_rec_avg_yac: { label: 'NG YAC', description: 'Average yards gained after the catch. Higher = more dangerous with the ball in hand.', format: 'decimal2' },
  ng_rec_avg_exp_yac: { label: 'NG Exp YAC', description: 'Expected yards after catch based on field position and defender proximity. Compare to actual YAC.', format: 'decimal2' },
  ng_rec_avg_yac_above_expectation: { label: 'NG YAC Over Exp', description: 'Actual minus expected YAC. Positive = creating extra yards beyond what the catch location would predict.', format: 'decimal2' },
  ng_rec_pct_share_of_intended_air_yds: { label: 'NG Air Share', description: 'Share of the team\'s total intended air yards directed at this receiver. Measures downfield target priority.', format: 'decimal2' },

  // Next Gen rushing profile.
  ng_rush_efficiency: { label: 'NG Rush Efficiency', description: 'Yards gained divided by yards expected based on blockers and defenders. Above 100% = beating blocks, below = underperforming.', format: 'decimal2' },
  ng_rush_avg_rush_yds: { label: 'NG Yds/Carry', description: 'Average yards per carry from Next Gen tracking data.', format: 'decimal2' },
  ng_rush_rush_yds_over_exp: { label: 'NG Yds Over Exp', description: 'Total rushing yards gained above what was expected based on blocking and defensive alignment. Shows true rushing skill.', format: 'decimal1' },
  ng_rush_rush_yds_over_exp_per_att: { label: 'NG Yds Over Exp/Att', description: 'Rushing yards over expectation per carry. The best per-play measure of rushing talent — removes O-line and scheme effects.', format: 'decimal2' },
  ng_rush_rush_pct_over_exp: { label: 'NG % Over Exp', description: 'Percentage of rushing yards gained above expectation. Separates runner skill from blocking quality.', format: 'decimal2' },
  ng_rush_avg_time_to_los: { label: 'NG Time To LOS', description: 'Average seconds to reach the line of scrimmage. Faster = more decisive; slower could mean dancing or bad blocking.', format: 'decimal2' },
  ng_rush_pct_att_gte_eight_defenders: { label: 'NG 8+ Box %', description: 'Percentage of carries facing 8+ defenders in the box. Higher = tougher rushing conditions, which makes gauging talent harder.', format: 'decimal1' },

  // PFR advanced detail stats.
  pfr_pass_pressure_pct: { label: 'PFR Pressure %', description: 'Percentage of dropbacks where the QB was pressured (hurried, hit, or sacked). Lower = better protection or quicker release.', format: 'decimal2' },
  pfr_pass_drop_pct: { label: 'PFR Drop %', description: 'Percentage of catchable passes dropped by receivers. Hurts QB stats without being the QB\'s fault.', format: 'decimal2' },
  pfr_pass_bad_throw_pct: { label: 'PFR Bad Throw %', description: 'Percentage of passes charted as uncatchable or poorly placed. Directly measures accuracy issues.', format: 'decimal2' },
  pfr_pass_times_pressured: { label: 'PFR Pressures', description: 'Total times the QB was pressured (sacked, hurried, or hit on a dropback).', format: 'decimal1' },
  pfr_rush_ybc_att: { label: 'PFR YBC/Att', description: 'Yards Before Contact per carry — how much yardage the O-line creates before a defender touches the runner.', format: 'decimal2' },
  pfr_rush_yac_att: { label: 'PFR YAC/Att', description: 'Yards After Contact per carry — yards gained after first defender contact. The best measure of a back\'s individual power and elusiveness.', format: 'decimal2' },
  pfr_rush_brk_tkl: { label: 'PFR Broken Tackles', description: 'Total broken tackles on rushing plays. Indicates physicality and ability to shed defenders.', format: 'decimal1' },
  pfr_rec_ybc_r: { label: 'PFR YBC/Rec', description: 'Yards Before Catch per reception — average distance the ball traveled in the air. Higher = more downfield targets.', format: 'decimal2' },
  pfr_rec_yac_r: { label: 'PFR YAC/Rec', description: 'Yards After Catch per reception — yards gained after securing the ball. Measures ability to create with the ball in hand.', format: 'decimal2' },
  pfr_rec_drop_pct: { label: 'PFR Rec Drop %', description: 'Percentage of catchable targets that were dropped. Lower = more reliable hands.', format: 'decimal2' },
  pfr_rec_brk_tkl: { label: 'PFR Rec Broken Tackles', description: 'Total broken tackles after receptions. Indicates YAC ability through contact.', format: 'decimal1' },

  // Derived interpretation percentiles.
  fp_ppr_pct: {label: 'PPR Percentile', description: 'Where this player ranks in PPR points among the same position. 90th = top 10% of the position group.', format: 'percent1'},
  pass_att_pct: {label: 'Pass Att Percentile', description: 'Percentile rank in passing volume vs other QBs. Higher = heavier passing workload.', format: 'percent1'},
  pass_yds_pct: {label: 'Pass Yds Percentile', description: 'Percentile rank in passing yards vs other QBs.', format: 'percent1'},
  rush_att_pct: {label: 'Rush Att Percentile', description: 'Percentile rank in rushing attempts vs same position. Higher = more featured in the run game.', format: 'percent1'},
  rush_yds_pct: {label: 'Rush Yds Percentile', description: 'Percentile rank in rushing yards vs same position.', format: 'percent1'},
  rec_yds_pct: {label: 'Rec Yds Percentile', description: 'Percentile rank in receiving yards vs same position.', format: 'percent1'},
  targets_pct: {label: 'Target Percentile', description: 'Percentile rank in targets vs same position. Higher = more involved in the passing game.', format: 'percent1'},
  exp_fp_pct: {label: 'Expected Pts Percentile', description: 'Percentile rank in expected fantasy points. High rank + low actual = underperformance to monitor.', format: 'percent1'},

  // Rate stats created in backend for convenience in UI.
  'Yds/Rec': {label: 'Yds/Rec', description: 'Yards per reception — total receiving yards divided by catches. Higher indicates big-play ability or deeper routes.', format: 'decimal1'},
  'Yds/Rush': {label: 'Yds/Rush', description: 'Yards per carry — total rushing yards divided by attempts. League average is around 4.3; elite backs hit 5.0+.', format: 'decimal1'},
};

// Shared default stat buckets for position-based fantasy tab grouping.
const CORE_STATS = ['fp_ppr', 'fp_std', 'exp_fp', 'volume_score'];
const PASSING_STATS = ['pass_att', 'pass_yds', 'pass_td', 'passing_first_downs'];
const RUSHING_STATS = ['rush_att', 'rush_yds', 'rush_td', 'Yds/Rush', 'rushing_first_downs'];
const RECEIVING_STATS = ['targets', 'rec', 'rec_yds', 'rec_td', 'Yds/Rec', 'receiving_first_downs'];

// Position-aware grouping map consumed by groupStatsByPosition.
export const POSITION_STAT_GROUPS = {
  Overall: {Core: CORE_STATS, Passing: PASSING_STATS, Rushing: RUSHING_STATS, Receiving: RECEIVING_STATS},
  QB: {Core: CORE_STATS, Passing: PASSING_STATS, Rushing: RUSHING_STATS},
  RB: {Core: CORE_STATS, Rushing: RUSHING_STATS, Receiving: RECEIVING_STATS},
  WR: {Core: CORE_STATS, Receiving: RECEIVING_STATS, Rushing: RUSHING_STATS},
  TE: {Core: CORE_STATS, Receiving: RECEIVING_STATS},
};
