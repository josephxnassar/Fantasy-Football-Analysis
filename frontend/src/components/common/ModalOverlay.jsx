/* Shared modal overlay — closes on backdrop click, passes through children. */

/**
 * @param {Object} props
 * @param {Function} props.onClose    — called when the backdrop (not content) is clicked
 * @param {string}  [props.className] — CSS class for the overlay div (default: "modal-overlay")
 * @param {React.ReactNode} props.children
 */
export default function ModalOverlay({ onClose, className = 'modal-overlay', children }) {
  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) onClose();
  };

  return (
    <div className={className} onClick={handleOverlayClick}>
      {children}
    </div>
  );
}
