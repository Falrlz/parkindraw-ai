import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react';

export type AlertType = 'info' | 'warning' | 'error' | 'success';

export interface AlertProps {
  type?: AlertType;
  title?: string;
  children: React.ReactNode;
  className?: string;
}

const alertConfig: Record<AlertType, { border: string; bg: string; text: string; icon: React.ReactNode }> = {
  info: {
    border: 'border-teal-200',
    bg: 'bg-teal-50',
    text: 'text-teal-900',
    icon: <Info className="w-5 h-5 text-teal-700 shrink-0 mt-0.5" aria-hidden="true" />,
  },
  warning: {
    border: 'border-amber-200',
    bg: 'bg-amber-50',
    text: 'text-amber-950',
    icon: <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" aria-hidden="true" />,
  },
  error: {
    border: 'border-rose-200',
    bg: 'bg-rose-50',
    text: 'text-rose-950',
    icon: <AlertCircle className="w-5 h-5 text-rose-700 shrink-0 mt-0.5" aria-hidden="true" />,
  },
  success: {
    border: 'border-emerald-200',
    bg: 'bg-emerald-50',
    text: 'text-emerald-950',
    icon: <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" aria-hidden="true" />,
  },
};

export const Alert: React.FC<AlertProps> = ({
  type = 'info',
  title,
  children,
  className = '',
}) => {
  const config = alertConfig[type];

  return (
    <div
      role="alert"
      className={`border rounded-lg p-3.5 sm:p-4 flex gap-3 ${config.border} ${config.bg} ${config.text} ${className}`}
    >
      {config.icon}
      <div className="flex-1 text-sm leading-relaxed">
        {title && <p className="font-semibold mb-1 text-inherit">{title}</p>}
        <div>{children}</div>
      </div>
    </div>
  );
};
