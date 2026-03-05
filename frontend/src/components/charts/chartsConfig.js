import { POSITION_OPTIONS, TOP_N_OPTIONS } from '../../utils/leaderboardOptions';

export { POSITION_OPTIONS, TOP_N_OPTIONS };

export const CHART_VIEW_OPTIONS = [
  { value: 'leaderboard', label: 'Leaderboard' },
  { value: 'consistency-upside', label: 'Average vs Upside' },
  { value: 'trend', label: 'Season Trends' },
];

export const VIEWS_USING_STAT = new Set(['leaderboard', 'trend']);

export const VIEW_META = {
  leaderboard: {
    kicker: 'Leaderboard View',
    description: 'Compare leaders by position, season, and key production metric. Advanced rate stats use minimum sample filters.',
  },
  'consistency-upside': {
    kicker: 'Average vs Upside',
    description: 'Compare weekly average output and weekly ceiling to find players who combine dependable points with game-breaking upside.',
  },
  trend: {
    kicker: 'Season Trends',
    description: 'Select one player and track the chosen stat across seasons to see long-term growth, decline, and stability.',
  },
};

// Default chart stat when switching positions.
export const DEFAULT_STAT = {
  QB: 'pass_yds',
  RB: 'rush_yds',
  WR: 'rec_yds',
  TE: 'rec_yds',
  Overall: 'fp_ppr',
};
