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
  if (typeof percentile !== 'number') return 'N/A';
  
  // Convert percentile to letter grade
  if (percentile >= 97) return 'A+';
  if (percentile >= 93) return 'A';
  if (percentile >= 90) return 'A-';
  if (percentile >= 87) return 'B+';
  if (percentile >= 83) return 'B';
  if (percentile >= 80) return 'B-';
  if (percentile >= 77) return 'C+';
  if (percentile >= 73) return 'C';
  if (percentile >= 70) return 'C-';
  if (percentile >= 67) return 'D+';
  if (percentile >= 63) return 'D';
  if (percentile >= 60) return 'D-';
  return 'F';
};

/**
 * Format stat value (integers vs decimals)
 */
export const formatStatValue = (value) => {
  if (typeof value !== 'number') return value;
  return Number.isInteger(value) ? value : value.toFixed(2);
};
