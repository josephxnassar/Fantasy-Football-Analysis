/* Shared modal overlay — closes on backdrop click, passes through children. */

import './ModalOverlay.css';

/**
 * @param {Object} props
 * @param {Function} props.onClose    — called when the backdrop (not content) is clicked
 * @param {string}  [props.className] — Optional modifier class for the overlay div
 * @param {React.ReactNode} props.children
 */
export default function ModalOverlay({ onClose, className = '', children }) {
  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) onClose();
  };
  const overlayClassName = ['modal-overlay', className].filter(Boolean).join(' ');

  return (
    <div className={overlayClassName} onClick={handleOverlayClick}>
      {children}
    </div>
  );
}
