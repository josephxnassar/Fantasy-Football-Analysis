/**
 * File overview: Component for Stat Tooltip within the shared UI layer.
 */

import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import './StatTooltip.css';

export default function StatTooltip({ label, description, iconSize = 12 }) {
  const [open, setOpen] = useState(false);
  const triggerRef = useRef(null);
  const popoverRef = useRef(null);
  const [coords, setCoords] = useState(null);

  useEffect(() => {
    if (!open) return;
    function handleClick(e) {
      if (popoverRef.current && !popoverRef.current.contains(e.target) && triggerRef.current && !triggerRef.current.contains(e.target))
        setOpen(false);
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [open]);

  useEffect(() => {
    if (!open) setCoords(null);
  }, [open]);

  useEffect(() => {
    if (!open || !popoverRef.current || !triggerRef.current) return;

    const edgePadding = 8;
    const gap = 6;
    const trigger = triggerRef.current.getBoundingClientRect();
    const popover = popoverRef.current.getBoundingClientRect();

    let top = trigger.bottom + gap;
    let left = trigger.left + trigger.width / 2 - popover.width / 2;

    const maxLeft = window.innerWidth - popover.width - edgePadding;
    left = Math.min(Math.max(left, edgePadding), Math.max(edgePadding, maxLeft));

    if (top + popover.height > window.innerHeight - edgePadding) top = trigger.top - popover.height - gap;
    if (top < edgePadding) top = edgePadding;

    setCoords((prev) => (prev?.top === top && prev?.left === left ? prev : { top, left }));
  }, [open, label, description]);

  if (!description) return null;

  return (
    <span className="stat-tooltip-wrap">
      <button
        ref={triggerRef}
        type="button"
        className="stat-tooltip-trigger"
        aria-label={`Info about ${label}`}
        onClick={(e) => {
          e.stopPropagation();
          setOpen((v) => !v);
        }}
      >
        <svg width={iconSize} height={iconSize} viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
          <text x="8" y="12" textAnchor="middle" fill="currentColor" fontSize="10" fontWeight="600">
            i
          </text>
        </svg>
      </button>
      {open &&
        createPortal(
          <div
            ref={popoverRef}
            className="stat-tooltip-popover"
            role="tooltip"
            style={coords ? { top: coords.top, left: coords.left } : { top: 0, left: 0, visibility: 'hidden', pointerEvents: 'none' }}
          >
            <div className="stat-tooltip-header">{label}</div>
            <div className="stat-tooltip-body">{description}</div>
          </div>,
          document.body,
        )}
    </span>
  );
}
