/* Shared stat-direction helpers for comparisons and ranking logic. */

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

export function isLowerBetterStat(statName) {
  const key = String(statName || '').trim().toLowerCase();
  return LOWER_IS_BETTER_TOKENS.some((token) => key.includes(token));
}
