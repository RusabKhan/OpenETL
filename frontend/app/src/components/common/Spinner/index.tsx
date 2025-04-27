// components/SpinnerToast.tsx
import React from "react";

interface SpinnerToastProps {
  message?: string;
  visible: boolean;
}

const Spinner: React.FC<SpinnerToastProps> = ({
  message = "Loading...",
  visible,
}) => {
  if (!visible) return null;

  return (
    <div className="fixed bottom-4 right-4 flex items-center space-x-4 rounded-lg bg-gray-800 px-6 py-3 text-white shadow-lg dark:bg-white dark:text-black">
      <div className="h-6 w-6 animate-spin rounded-full border-t-2 border-white dark:border-black"></div>
      <span>{message}</span>
    </div>
  );
};

export default Spinner;
