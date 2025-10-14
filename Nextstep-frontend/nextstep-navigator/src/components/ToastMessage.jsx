import React, { useEffect } from 'react';

export default function ToastMessage({ show, message = '', variant = 'success', duration = 3000, onClose }) {
  useEffect(() => {
    if (!show) return;
    const t = setTimeout(() => {
      onClose && onClose();
    }, duration);
    return () => clearTimeout(t);
  }, [show, duration, onClose]);

  if (!show) return null;

  const bg = variant === 'success' ? 'bg-success text-white' : variant === 'danger' ? 'bg-danger text-white' : 'bg-secondary text-white';

  return (
    <div aria-live="polite" aria-atomic="true" style={{ position: 'fixed', top: 20, right: 20, zIndex: 1060 }}>
      <div className={`toast show ${bg}`} role="alert" aria-live="assertive" aria-atomic="true" style={{ minWidth: 200 }}>
        <div className="d-flex">
          <div className="toast-body">{message}</div>
          <button
            type="button"
            className="btn-close me-2 m-auto"
            aria-label="Close"
            onClick={() => onClose && onClose()}
            style={{ filter: 'invert(1)'}}
          />
        </div>
      </div>
    </div>
  );
}
