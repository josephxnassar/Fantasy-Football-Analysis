// Backdrop clicks close the modal.

import './ModalBackdrop.css';

export default function ModalBackdrop({ onClose, className = '', children }) {
  const handleOverlayClick = (e) => {if (e.target === e.currentTarget) onClose()};
  const overlayClassName = ['modal-overlay', className].filter(Boolean).join(' ');
  return (<div className={overlayClassName} onClick={handleOverlayClick}>{children}</div>);
}
