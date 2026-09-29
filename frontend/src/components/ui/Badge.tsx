import React from 'react';

export type BadgeVariant = 'healthy' | 'parkinson' | 'info' | 'neutral' | 'error';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  children: React.ReactNode;
}

const variantStyles: Record<BadgeVariant, { chip: string; dot: string }> = {
  healthy: { chip: 'bg-aqua-wash text-aqua-deep', dot: 'bg-aqua-deep' },
  parkinson: { chip: 'bg-amber-wash text-amber-ink', dot: 'bg-amber-ink' },
  info: { chip: 'bg-iris-wash text-iris-deep', dot: 'bg-iris' },
  neutral: { chip: 'bg-ground text-body', dot: 'bg-muted' },
  error: { chip: 'bg-rose-wash text-rose-ink', dot: 'bg-rose-ink' },
};

export const Badge: React.FC<BadgeProps> = ({
  variant = 'neutral',
  children,
  className = '',
  ...props
}) => {
  const style = variantStyles[variant];
  return (
    <span
      {...props}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${style.chip} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} aria-hidden="true" />
      {children}
    </span>
  );
};
