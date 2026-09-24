import React from 'react';

export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'outline' | 'ghost';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: 'bg-teal-700 text-white hover:bg-teal-800 border border-teal-700 disabled:bg-slate-300 disabled:border-slate-300 disabled:text-slate-500',
  secondary: 'bg-slate-100 text-slate-800 hover:bg-slate-200 border border-slate-300 disabled:bg-slate-50 disabled:text-slate-400',
  danger: 'bg-rose-700 text-white hover:bg-rose-800 border border-rose-700 disabled:bg-slate-300 disabled:border-slate-300',
  outline: 'bg-transparent text-slate-700 hover:bg-slate-100 border border-slate-300 disabled:text-slate-400 disabled:border-slate-200',
  ghost: 'bg-transparent text-slate-700 hover:bg-slate-100 border border-transparent disabled:text-slate-400',
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-4 py-2 text-sm',
  lg: 'px-5 py-2.5 text-base font-semibold',
};

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  disabled,
  className = '',
  ...props
}) => {
  return (
    <button
      {...props}
      disabled={disabled || isLoading}
      className={`inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors cursor-pointer disabled:cursor-not-allowed ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
    >
      {isLoading ? (
        <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" aria-hidden="true" />
      ) : (
        leftIcon
      )}
      <span>{children}</span>
      {!isLoading && rightIcon}
    </button>
  );
};
