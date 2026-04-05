import React, { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: number;
  type: ToastType;
  message: string;
}

interface ToastContextType {
  toasts: Toast[];
  toast: (type: ToastType, message: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

let nextId = 0;

export const ToastProvider = ({ children }: { children: ReactNode }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((type: ToastType, message: string) => {
    const id = nextId++;
    setToasts((prev) => [...prev.slice(-2), { id, type, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, toast: addToast }}>
      {children}
      {/* Toast Container */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 pointer-events-none">
        {toasts.map((t) => {
          const colors: Record<ToastType, string> = {
            success: 'bg-accent-green/15 border-accent-green/30 text-accent-green',
            error: 'bg-accent-red/15 border-accent-red/30 text-accent-red',
            warning: 'bg-accent-yellow/15 border-accent-yellow/30 text-accent-yellow',
            info: 'bg-accent-blue/15 border-accent-blue/30 text-accent-blue',
          };
          return (
            <div
              key={t.id}
              className={`pointer-events-auto px-5 py-3 rounded-lg border backdrop-blur-md text-sm font-medium shadow-lg animate-in slide-in-from-right-4 duration-300 ${colors[t.type]}`}
            >
              {t.message}
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within a ToastProvider');
  return ctx;
};
