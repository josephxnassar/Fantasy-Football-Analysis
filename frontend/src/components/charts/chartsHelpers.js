import { getStatLabel } from '../../utils/statDefinitions';
import { meetsStatThreshold } from '../../utils/statThresholds';

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

function isFiniteNumber(value) {
  return typeof value === 'number' && Number.isFinite(value);
}

export function buildPlayerTrendSeries(seasonPayloads = [], playerName, stat) {
  if (!Array.isArray(seasonPayloads) || !playerName) return [];
  return seasonPayloads
    .slice()
    .sort((a, b) => a.season - b.season)
    .map((seasonPayload) => {
      const player = (seasonPayload.players || []).find((seasonPlayer) => seasonPlayer.name === playerName);
      const value = player?.stats?.[stat];
      return {
        season: seasonPayload.season,
        value: isFiniteNumber(value) ? value : null,
      };
    });
}

export function getChartHeight(rowCount) {
  // Dynamic sizing avoids clipping labels as row count grows.
  return Math.max(400, rowCount * 32 + 60);
}
