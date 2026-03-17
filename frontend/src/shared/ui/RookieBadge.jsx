/**
 * File overview: Component for Rookie Badge within the shared UI layer.
 */

import './RookieBadge.css';

export default function RookieBadge({ isRookie, size = 'medium' }) {
  if (!isRookie) return null;
  return <span className={`rookie-badge rookie-badge-${size}`}>R</span>;
}
