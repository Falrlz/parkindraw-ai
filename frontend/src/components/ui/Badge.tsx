import React from 'react';

export type BadgeVariant = 'healthy' | 'parkinson' | 'info' | 'neutral' | 'error';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  children: React.ReactNode;
}

const variantStyles: Record<BadgeVariant, string> = {
  healthy: 'bg-emerald-50 text-emerald-800 border-emerald-300',
  parkinson: 'bg-amber-50 text-amber-900 border-amber-300',
  info: 'bg-teal-50 text-teal-800 border-teal-300',
  neutral: 'bg-slate-100 text-slate-700 border-slate-300',
  error: 'bg-rose-50 text-rose-800 border-rose-300',
};

export const Badge: React.FC<BadgeProps> = ({
  variant = 'neutral',
  children,
  className = '',
  ...props
}) => {
  return (
    <span
      {...props}
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
};
