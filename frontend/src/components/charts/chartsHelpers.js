import { getStatLabel } from '../../utils/statDefinitions';
import { POSITION_OPTIONS, TOP_N_OPTIONS } from '../../utils/leaderboardOptions';
import { meetsStatThreshold } from '../../utils/statThresholds';

export { POSITION_OPTIONS, TOP_N_OPTIONS };

// Default chart stat when switching positions.
export const DEFAULT_STAT = {
  QB: 'pass_yds',
  RB: 'rush_yds',
  WR: 'rec_yds',
  TE: 'rec_yds',
  Overall: 'fp_ppr',
};

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
  if (!Array.isArray(players)) return [];
  return players
    .filter((player) => player.stats[stat] != null && meetsStatThreshold(player, stat))
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
