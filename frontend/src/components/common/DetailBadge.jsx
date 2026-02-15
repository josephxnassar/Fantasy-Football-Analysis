/* Reusable badge for displaying player details (team, position, age) */

import './DetailBadge.css';

export default function DetailBadge({ children }) {
  return <span className="detail detail-badge">{children}</span>;
}
