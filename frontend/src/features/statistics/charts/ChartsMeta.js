/**
 * File overview: Chart-view metadata and default selections for the statistics charts feature.
 */

export const CHART_VIEW_OPTIONS = [
  { value: 'leaderboard', label: 'Leaderboard' },
  { value: 'consistency-upside', label: 'Average vs Upside' },
  { value: 'trend', label: 'Season Trends' },
];

// Only leaderboard and season trends expose a stat selector. Average vs Upside
// has a fixed axis pairing, so the screen hides that control for the view.
export const VIEWS_USING_STAT = new Set(['leaderboard', 'trend']);

export const VIEW_META = {
  leaderboard: {
    kicker: 'Leaderboard View',
    description: 'Compare leaders by position, season, and key production metric. Advanced rate stats use minimum sample filters.',
  },
  'consistency-upside': {
    kicker: 'Average vs Upside',
    description:
      'Compare weekly average output and weekly ceiling to find players who combine dependable points with game-breaking upside. Points closer to the top-right are better.',
  },
  trend: {
    kicker: 'Season Trends',
    description:
      'Select one player and track the chosen stat across seasons. The stat categories automatically adapt to the selected player’s position.',
  },
};

export const DEFAULT_STAT = {
  QB: 'pass_yds',
  RB: 'rush_yds',
  WR: 'rec_yds',
  TE: 'rec_yds',
  Overall: 'fp_ppr',
};
