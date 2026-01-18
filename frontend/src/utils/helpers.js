/**
 * Utility functions for the Fantasy Football Analysis app
 */

/**
 * Extract player name from player object (handles different name formats)
 */
export const getPlayerName = (player) => {
  return player.name || player[Object.keys(player)[0]];
};

/**
 * Format percentile value for display
 */
export const formatPercentile = (percentile) => {
  return typeof percentile === 'number' ? `${Math.round(percentile)}%` : 'N/A';
};

/**
 * Format stat value (integers vs decimals)
 */
export const formatStatValue = (value) => {
  if (typeof value !== 'number') return value;
  return Number.isInteger(value) ? value : value.toFixed(2);
};
