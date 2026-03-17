/**
 * File overview: Component for Detail Badge within the shared UI layer.
 */

import './DetailBadge.css';

export default function DetailBadge({ children }) {
  return <span className="detail detail-badge">{children}</span>;
}
