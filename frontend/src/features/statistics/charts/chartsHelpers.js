import { getStatLabel } from '../../../shared/utils/statDefinitions';
import { meetsStatThreshold } from '../../../shared/utils/statThresholds';
import { PLAYER_DISPLAY_LIMIT } from '../statisticsOptions';

export function getStatOptions(position, statColumns = [], positionStatGroups) {
  const groups = positionStatGroups[position];
  if (!groups) return [];
  return Object.entries(groups)
    .map(([category, stats]) => ({ category, stats: stats.filter((stat) => statColumns.includes(stat)) }))
    .filter(({ stats }) => stats.length > 0);
}

export function buildBarData(players = [], stat, limit = PLAYER_DISPLAY_LIMIT) {
  if (!Array.isArray(players)) return [];
  return players
    .filter((player) => player.stats[stat] != null && meetsStatThreshold(player, stat))
    .map((player) => ({
      statKey: stat,
      name: player.name,
      position: player.position,
      team: player.team,
      headshot_url: player.headshot_url,
      value: player.stats[stat],
      statLabel: getStatLabel(stat),
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, limit);
}

export function getChartHeight(rowCount) {
  return Math.max(400, rowCount * 32 + 60);
}
