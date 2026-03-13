// Shared modal overlay with backdrop-close behavior.

import './ModalOverlay.css';

export default function ModalOverlay({ onClose, className = '', children }) {
  // Only backdrop clicks close the modal; content clicks are ignored.
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
