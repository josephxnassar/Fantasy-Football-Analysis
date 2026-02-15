/* Stat color-coding helpers (similar to Sleeper) - Returns CSS class based on stat performance thresholds */

// Define thresholds for "good" performance (green) - using display names
const STAT_THRESHOLDS = {
  // Passing (QB)
  'Pass Yds': 300,
  'Pass TD': 3,
  'Comp': 25,
  'Att': 35,
  
  // Rushing (RB/QB)
  'Rush Yds': 100,
  'Rush TD': 1,
  'Carries': 20,
  'Yds/Rush': 5,
  
  // Receiving (WR/TE/RB)
  'Rec': 8,
  'Rec Yds': 100,
  'Rec TD': 1,
  'Tgt': 10,
  'Yds/Rec': 12,
  'Rec YAC': 50,
  
  // Advanced stats
  'Pass EPA': 5,
  'Rush EPA': 2,
  'Rec EPA': 2,
  
  // Fantasy Points
  'PPR Pts': 20,
  'Snap Share': 70,
};

// Stats where lower is better (red for high values) - using display names
const LOWER_IS_BETTER = new Set([
  'INT',
  'Sacks',
  'Sack Fum',
  'Rush Fum',
  'Rush Fum Lost',
  'Rec Fum',
  'Rec Fum Lost'
]);

/**
 * Get color class for a stat value
 * @param {string} statName - The stat key
 * @param {number} value - The stat value
 * @returns {string} - CSS class: 'stat-good', 'stat-medium', 'stat-poor', or ''
 */
export function getStatColorClass(statName, value) {
  if (value === null || value === undefined) return '';
  const normalizedValue = statName === 'Snap Share' && value <= 1 ? value * 100 : value;
  
  // Handle lower-is-better stats (turnovers, etc)
  if (LOWER_IS_BETTER.has(statName)) {
    if (value === 0) return 'stat-good';
    if (value === 1) return 'stat-medium';
    if (value >= 2) return 'stat-poor';
    return '';
  }
  
  // Handle normal stats (higher is better)
  const threshold = STAT_THRESHOLDS[statName];
  if (!threshold) return '';
  
  if (normalizedValue >= threshold) {
    return 'stat-good';
  } else if (normalizedValue >= threshold * 0.5) {
    return 'stat-medium';
  } else {
    return 'stat-poor';
  }
}
