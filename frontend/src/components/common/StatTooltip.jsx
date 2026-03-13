import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import './StatTooltip.css';

export default function StatTooltip({ label, description, iconSize = 12 }) {
  const [open, setOpen] = useState(false);
  const triggerRef = useRef(null);
  const popoverRef = useRef(null);
  const [coords, setCoords] = useState(null);

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

  // Position the fixed popover relative to the trigger.
  useEffect(() => {
    if (!open || !triggerRef.current) return;
    const trigger = triggerRef.current.getBoundingClientRect();
    const popW = 260; // matches CSS width
    const gap = 6;

    // Prefer below the trigger, centered.
    let top = trigger.bottom + gap;
    let left = trigger.left + trigger.width / 2 - popW / 2;

    // Clamp horizontally.
    if (left < 8) left = 8;
    if (left + popW > window.innerWidth - 8) left = window.innerWidth - popW - 8;

    // If it would overflow the bottom, flip above. Estimate popover height (will be corrected on next frame).
    const estH = 120;
    if (top + estH > window.innerHeight - 8) {
      top = trigger.top - estH - gap;
    }

    setCoords({ top, left });
  }, [open]);

  // After render, refine vertical position with actual height.
  useEffect(() => {
    if (!open || !popoverRef.current || !triggerRef.current) return;
    const pop = popoverRef.current.getBoundingClientRect();
    const trigger = triggerRef.current.getBoundingClientRect();
    const gap = 6;
    if (pop.bottom > window.innerHeight - 8) {
      setCoords((prev) => ({
        ...prev,
        top: trigger.top - pop.height - gap,
      }));
    }
  }, [open, coords?.top]);

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
        <svg width={iconSize} height={iconSize} viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
          <text x="8" y="12" textAnchor="middle" fill="currentColor" fontSize="10" fontWeight="600">i</text>
        </svg>
      </button>

      {open && coords && createPortal(
        <div
          ref={popoverRef}
          className="stat-tooltip-popover"
          role="tooltip"
          style={{ top: coords.top, left: coords.left }}
        >
          <div className="stat-tooltip-header">{label}</div>
          <div className="stat-tooltip-body">{description}</div>
        </div>,
        document.body,
      )}
    </span>
  );
}
