import { useEffect } from "react";
import "../styles/notification.css";

function Notification({ message, type, onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className={`notification notification-${type}`}>
      <div className="notification-content">
        {type === "success" && <span className="notification-icon">✓</span>}
        {type === "error" && <span className="notification-icon">✕</span>}
        {type === "loading" && <span className="notification-icon loading">⟳</span>}
        <span className="notification-message">{message}</span>
      </div>
    </div>
  );
}

export default Notification;
