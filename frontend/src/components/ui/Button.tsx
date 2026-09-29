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
  primary:
    'bg-iris text-on-iris border border-iris hover:bg-iris-deep hover:border-iris-deep active:bg-ink-fill active:border-ink-fill active:text-white disabled:bg-line disabled:border-line disabled:text-muted',
  secondary:
    'bg-iris-wash text-ink border border-transparent hover:bg-lilac/40 disabled:bg-ground disabled:text-muted',
  danger:
    'bg-rose-ink text-on-iris border border-rose-ink hover:opacity-90 disabled:bg-line disabled:border-line disabled:text-muted',
  outline:
    'bg-paper text-iris border border-iris hover:bg-iris-wash active:border-ink active:text-ink disabled:text-muted disabled:border-line disabled:bg-paper',
  ghost:
    'bg-transparent text-ink border border-transparent hover:bg-iris-wash disabled:text-muted',
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'min-h-10 px-3.5 text-sm',
  md: 'min-h-12 px-5 text-[15px]',
  lg: 'min-h-14 px-7 text-base',
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
      aria-busy={isLoading || undefined}
      className={`group/btn inline-flex items-center justify-center gap-2.5 rounded-md font-medium tracking-[-0.005em] transition-[background-color,border-color,color,transform] duration-200 ease-out cursor-pointer active:translate-y-px disabled:cursor-not-allowed disabled:active:translate-y-0 ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
    >
      {isLoading ? (
        <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" aria-hidden="true" />
      ) : (
        leftIcon
      )}
      <span>{children}</span>
      {!isLoading && rightIcon && (
        <span className="inline-flex transition-transform duration-200 ease-out group-hover/btn:translate-x-0.5">
          {rightIcon}
        </span>
      )}
    </button>
  );
};
