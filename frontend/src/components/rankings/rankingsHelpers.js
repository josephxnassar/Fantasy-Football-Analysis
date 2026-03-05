import { meetsStatThreshold } from '../../utils/statThresholds';

export const DEFAULT_CATEGORY_WEIGHT = 1;
export const DEFAULT_STAT_WEIGHT = 0;
export const WEIGHT_STEPS = [-2, -1, 0, 1, 2];

export const WEIGHT_LABELS = {
  '-2': 'Much Less',
  '-1': 'Less',
  0: 'Neutral',
  1: 'More',
  2: 'Much More',
};

const LOWER_IS_BETTER_TOKENS = [
  'interception',
  '_int',
  'fumble',
  'drop',
  'bad_throw',
  'times_sacked',
  'times_pressured',
  'pressure_pct',
  '_rank',
];

function isLowerBetter(stat) {
  const key = String(stat || '').toLowerCase();
  return LOWER_IS_BETTER_TOKENS.some((token) => key.includes(token));
}

function toNumber(value) {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

export function getRankableGroups(position, statColumns = [], rankingGroups) {
  const groups = rankingGroups[position];
  if (!groups) return [];
  return Object.entries(groups)
    .map(([category, stats]) => ({
      category,
      stats: stats.filter((stat) => statColumns.includes(stat)),
    }))
    .filter(({ stats }) => stats.length > 0);
}

export function buildRankings(
  players = [],
  rankableGroups,
  categoryWeights = {},
  statWeights = {},
  topN = 20
) {
  if (!Array.isArray(players) || players.length === 0) return [];

  const weightedStats = rankableGroups.flatMap(({ category, stats }) =>
    stats
      .map((stat) => {
        const categoryWeight = categoryWeights[category] ?? DEFAULT_CATEGORY_WEIGHT;
        const statWeight = statWeights[stat] ?? DEFAULT_STAT_WEIGHT;
        const weight = categoryWeight + statWeight;
        return { category, stat, weight };
      })
      .filter(({ weight }) => weight !== 0)
  );

  if (!weightedStats.length) return [];

  const statRanges = new Map();

  for (const { stat } of weightedStats) {
    const values = players
      .map((player) => {
        const value = toNumber(player?.stats?.[stat]);
        if (value === null || !meetsStatThreshold(player, stat)) return null;
        return value;
      })
      .filter((value) => value !== null);
    if (!values.length) continue;
    statRanges.set(stat, {
      min: Math.min(...values),
      max: Math.max(...values),
      lowerIsBetter: isLowerBetter(stat),
    });
  }

  const ranked = players
    .map((player) => {
      let score = 0;
      let totalWeight = 0;

      for (const { stat, weight } of weightedStats) {
        const range = statRanges.get(stat);
        if (!range) continue;
        const value = toNumber(player?.stats?.[stat]);
        if (value === null || !meetsStatThreshold(player, stat)) continue;

        let normalized = range.max === range.min ? 0.5 : (value - range.min) / (range.max - range.min);
        if (range.lowerIsBetter) {
          normalized = 1 - normalized;
        }

        score += normalized * weight;
        totalWeight += Math.abs(weight);
      }

      if (totalWeight === 0) return null;

      return {
        name: player.name,
        team: player.team,
        position: player.position,
        age: player.age,
        score: score / totalWeight,
      };
    })
    .filter(Boolean)
    .sort((a, b) => b.score - a.score)
    .slice(0, topN)
    .map((player, index) => ({
      ...player,
      rank: index + 1,
    }));

  return ranked;
}
