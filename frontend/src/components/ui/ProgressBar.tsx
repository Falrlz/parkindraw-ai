import React from 'react';

export interface ProgressBarProps {
  value: number; // 0 - 100
  label?: string;
  showPercentage?: boolean;
  color?: 'teal' | 'amber' | 'emerald' | 'rose';
  className?: string;
}

const colorStyles = {
  teal: 'bg-teal-700',
  amber: 'bg-amber-600',
  emerald: 'bg-emerald-600',
  rose: 'bg-rose-600',
};

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  label,
  showPercentage = true,
  color = 'teal',
  className = '',
}) => {
  const clampedValue = Math.min(100, Math.max(0, value));

  return (
    <div className={`w-full ${className}`}>
      {(label || showPercentage) && (
        <div className="flex justify-between items-center mb-1.5 text-xs font-semibold text-slate-700">
          <span>{label}</span>
          {showPercentage && <span>{clampedValue.toFixed(1)}%</span>}
        </div>
      )}
      <div
        role="progressbar"
        aria-valuenow={clampedValue}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label || 'Progress bar'}
        className="w-full h-2.5 bg-slate-200 rounded-full overflow-hidden"
      >
        <div
          className={`h-full transition-all duration-300 ${colorStyles[color]}`}
          style={{ width: `${clampedValue}%` }}
        />
      </div>
    </div>
  );
};
