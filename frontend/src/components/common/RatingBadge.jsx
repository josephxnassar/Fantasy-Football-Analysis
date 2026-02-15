/* Reusable rating display badge component */

import './RatingBadge.css';

export default function RatingBadge({ rating, label = 'Rating' }) {
  return (
    <span className="detail detail-rating">
      {label}: {typeof rating === 'number' ? rating.toFixed(2) : rating}
    </span>
  );
}
