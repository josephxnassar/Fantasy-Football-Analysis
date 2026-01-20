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

/**
 * Format percentile as ordinal (e.g., "98th percentile"), capped at 99th
 */
export const formatOrdinalPercentile = (percentile) => {
  if (typeof percentile !== 'number' || isNaN(percentile)) return 'N/A';
  
  // Cap at 99th percentile
  const capped = Math.min(Math.round(percentile), 99);
  
  // Get ordinal suffix
  const lastDigit = capped % 10;
  const lastTwoDigits = capped % 100;
  let suffix = 'th';
  
  if (lastTwoDigits >= 11 && lastTwoDigits <= 13) {
    suffix = 'th';
  } else if (lastDigit === 1) {
    suffix = 'st';
  } else if (lastDigit === 2) {
    suffix = 'nd';
  } else if (lastDigit === 3) {
    suffix = 'rd';
  }
  
  return `${capped}${suffix} percentile`;
};
