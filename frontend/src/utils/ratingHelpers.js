/* Utility functions for rating calculations and formatting */

export const getRatingValue = (player, format = 'redraft') => {
  const ratingField = format === 'dynasty' ? 'DynastyRating' : 'RedraftRating';
  const rating = player[ratingField];
  return typeof rating === 'number' ? rating.toFixed(2) : 'N/A';
};

export const sortPlayersByRating = (players, format = 'redraft') => {
  const ratingField = format === 'dynasty' ? 'DynastyRating' : 'RedraftRating';
  return [...players].sort((a, b) => (b[ratingField] || 0) - (a[ratingField] || 0));
};
