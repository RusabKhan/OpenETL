import React, { useEffect } from "react";

interface ToastProps {
  message: string;
  type?: "success" | "error" | "warning" | "info";
  visible: boolean;
  onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({
  message,
  type = "success",
  visible,
  onClose,
}) => {
  useEffect(() => {
    if (visible) {
      const timer = setTimeout(onClose, 3000); // Auto-dismiss after 3 seconds
      return () => clearTimeout(timer);
    }
  }, [visible, onClose]);

  if (!visible) return null;

  const toastStyles: Record<typeof type, string> = {
    success: "bg-green-500 text-white",
    error: "bg-red-500 text-white",
    warning: "bg-yellow-500 text-black",
    info: "bg-blue-500 text-white",
  };

  if (message !== "Request was canceled.") {
    return (
      <div
        className={`fixed bottom-4 right-4 transform rounded-lg px-6 py-3 shadow-lg transition-transform ${
          visible ? "scale-100" : "scale-0"
        } ${toastStyles[type]}`}
      >
        {message}
      </div>
    );
  }
};

export default Toast;
