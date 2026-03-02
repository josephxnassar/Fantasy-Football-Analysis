import { useEffect, useRef, useState } from 'react';
import './StatTooltip.css';

/**
 * Rich tooltip popover for stat explanations.
 * Triggered by clicking an info icon next to a stat label.
 * Auto-positions to stay within the viewport.
 */
export default function StatTooltip({ label, description }) {
  const [open, setOpen] = useState(false);
  const triggerRef = useRef(null);
  const popoverRef = useRef(null);

  // Close when clicking outside.
  useEffect(() => {
    if (!open) return;
    function handleClick(e) {
      if (
        popoverRef.current && !popoverRef.current.contains(e.target) &&
        triggerRef.current && !triggerRef.current.contains(e.target)
      ) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [open]);

  // Auto-nudge popover if it overflows the viewport.
  useEffect(() => {
    if (!open || !popoverRef.current) return;
    const rect = popoverRef.current.getBoundingClientRect();
    if (rect.right > window.innerWidth - 8) {
      popoverRef.current.style.left = 'auto';
      popoverRef.current.style.right = '0';
    }
    if (rect.bottom > window.innerHeight - 8) {
      popoverRef.current.style.top = 'auto';
      popoverRef.current.style.bottom = '100%';
      popoverRef.current.style.marginBottom = '6px';
    }
  }, [open]);

  if (!description) return null;

  return (
    <span className="stat-tooltip-wrap">
      <button
        ref={triggerRef}
        type="button"
        className="stat-tooltip-trigger"
        aria-label={`Info about ${label}`}
        onClick={(e) => { e.stopPropagation(); setOpen((v) => !v); }}
      >
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
          <text x="8" y="12" textAnchor="middle" fill="currentColor" fontSize="10" fontWeight="600">i</text>
        </svg>
      </button>

      {open && (
        <div ref={popoverRef} className="stat-tooltip-popover" role="tooltip">
          <div className="stat-tooltip-header">{label}</div>
          <div className="stat-tooltip-body">{description}</div>
        </div>
      )}
    </span>
  );
}
