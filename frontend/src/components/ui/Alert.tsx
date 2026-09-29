import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react';

export type AlertType = 'info' | 'warning' | 'error' | 'success';

export interface AlertProps {
  type?: AlertType;
  title?: string;
  children: React.ReactNode;
  className?: string;
}

const alertConfig: Record<AlertType, { surface: string; title: string; icon: React.ReactNode }> = {
  info: {
    surface: 'bg-iris-wash border-iris/25 text-ink',
    title: 'text-iris-deep',
    icon: <Info className="w-5 h-5 text-iris shrink-0 mt-0.5" strokeWidth={1.75} aria-hidden="true" />,
  },
  warning: {
    surface: 'bg-amber-wash border-amber-line text-ink',
    title: 'text-amber-ink',
    icon: <AlertTriangle className="w-5 h-5 text-amber-ink shrink-0 mt-0.5" strokeWidth={1.75} aria-hidden="true" />,
  },
  error: {
    surface: 'bg-rose-wash border-rose-ink/25 text-ink',
    title: 'text-rose-ink',
    icon: <AlertCircle className="w-5 h-5 text-rose-ink shrink-0 mt-0.5" strokeWidth={1.75} aria-hidden="true" />,
  },
  success: {
    surface: 'bg-aqua-wash border-aqua-deep/25 text-ink',
    title: 'text-aqua-deep',
    icon: <CheckCircle2 className="w-5 h-5 text-aqua-deep shrink-0 mt-0.5" strokeWidth={1.75} aria-hidden="true" />,
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
      className={`border rounded-[10px] p-4 sm:p-5 flex gap-3.5 ${config.surface} ${className}`}
    >
      {config.icon}
      <div className="flex-1 text-[15px] leading-relaxed">
        {title && <p className={`font-semibold mb-1 ${config.title}`}>{title}</p>}
        <div>{children}</div>
      </div>
    </div>
  );
};
