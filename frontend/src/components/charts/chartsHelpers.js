import { getStatLabel } from '../../utils/statDefinitions';

// Default chart stat when switching positions.
export const DEFAULT_STAT = {
  QB: 'pass_yds',
  RB: 'rush_yds',
  WR: 'rec_yds',
  TE: 'rec_yds',
  Overall: 'fp_ppr',
};

export const POSITION_OPTIONS = ['Overall', 'QB', 'RB', 'WR', 'TE'];

// Derived rate stats need minimum volume before we chart them.
const DERIVED_STAT_THRESHOLDS = {
  'Yds/Rush': { volumeStats: ['rush_att', 'carries'], minVolume: 100 },
  'Yds/Rec': { volumeStats: ['rec', 'receptions'], minVolume: 50 },
};

// Guard derived rates from tiny-sample noise.
function meetsDerivedThreshold(player, stat) {
  const threshold = DERIVED_STAT_THRESHOLDS[stat];
  if (!threshold) return true;
  const volume = threshold.volumeStats
    .map((key) => player?.stats?.[key])
    .find((value) => typeof value === 'number');
  return typeof volume === 'number' && volume >= threshold.minVolume;
}

export function getStatOptions(position, statColumns = [], positionStatGroups) {
  // Keeps the stat picker aligned with what backend actually returned.
  const groups = positionStatGroups[position];
  if (!groups) return [];
  return Object.entries(groups)
    .map(([category, stats]) => ({
      category,
      stats: stats.filter((stat) => statColumns.includes(stat)),
    }))
    .filter(({ stats }) => stats.length > 0);
}

export function buildBarData(players = [], stat, topN) {
  // Normalize player rows into bar-chart payload + top-N ordering.
  if (!Array.isArray(players)) return [];
  return players
    .filter((player) => player.stats[stat] != null && meetsDerivedThreshold(player, stat))
    .map((player) => ({
      name: player.name,
      position: player.position,
      team: player.team,
      headshot_url: player.headshot_url,
      value: player.stats[stat],
      statLabel: getStatLabel(stat),
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, topN);
}

export function getChartHeight(rowCount) {
  // Dynamic sizing avoids clipping labels as row count grows.
  return Math.max(400, rowCount * 32 + 60);
}
