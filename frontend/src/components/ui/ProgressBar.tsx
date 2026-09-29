import React from 'react';

export interface ProgressBarProps {
  value: number; // 0 - 100
  label?: string;
  showPercentage?: boolean;
  color?: 'teal' | 'amber' | 'emerald' | 'rose';
  /** Optional marker (0-100) drawn as a tick on the scale, e.g. the decision threshold. */
  marker?: number;
  className?: string;
}

const colorStyles = {
  teal: 'bg-iris',
  amber: 'bg-amber-rule',
  emerald: 'bg-aqua-rule',
  rose: 'bg-rose-ink',
};

/** A measured scale: hairline track, filled rule, optional threshold tick. */
export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  label,
  showPercentage = true,
  color = 'teal',
  marker,
  className = '',
}) => {
  const clampedValue = Math.min(100, Math.max(0, value));

  return (
    <div className={`w-full ${className}`}>
      {(label || showPercentage) && (
        <div className="flex justify-between items-baseline gap-3 mb-2 text-sm text-body">
          <span>{label}</span>
          {showPercentage && (
            <span className="tabular font-medium text-ink">{clampedValue.toFixed(1)}%</span>
          )}
        </div>
      )}
      <div
        role="progressbar"
        aria-valuenow={Number(clampedValue.toFixed(1))}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label || 'Progress bar'}
        className="relative w-full h-2 bg-line rounded-full"
      >
        <div
          className={`h-full rounded-full transition-[width] duration-700 ease-out ${colorStyles[color]}`}
          style={{ width: `${clampedValue}%` }}
        />
        {marker !== undefined && (
          <span
            className="absolute -top-1.5 w-px h-5 bg-ink"
            style={{ left: `${Math.min(100, Math.max(0, marker))}%` }}
            aria-hidden="true"
          />
        )}
      </div>
    </div>
  );
};
