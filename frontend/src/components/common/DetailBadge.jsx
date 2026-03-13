// Reusable badge for player details like team, position, and age.

import './DetailBadge.css';

export default function DetailBadge({ children }) {
  return <span className="detail detail-badge">{children}</span>;
}
