import React, { useId, useMemo } from 'react';
import { jitter, meanderPoints, spiralPoints, toPath } from './spiral';

export interface RibbonProps {
  className?: string;
  /** 'draw' writes the stroke once on mount; 'loop' breathes continuously (loading states). */
  motion?: 'draw' | 'loop' | 'none';
  /** Number of hairlines in the ribbon sheaf. */
  density?: number;
  /** Show the single ink line, the "hand-drawn specimen", over the sheaf. */
  showInk?: boolean;
}

/**
 * The emblem: a translucent sheaf of hairlines (teal → lilac → violet) that
 * winds as a spiral and leaves as a meander. Drawn, never painted: every line
 * is an SVG stroke so it stays crisp and animates as a pen would.
 */
export const Ribbon: React.FC<RibbonProps> = ({
  className = '',
  motion = 'draw',
  density = 26,
  showInk = true,
}) => {
  const gradientId = useId().replace(/:/g, '');

  const { sheaf, ink } = useMemo(() => {
    const spiral = spiralPoints(420, 470, 3.25, 10, 15.5);
    const end = spiral[spiral.length - 1];
    const tail = meanderPoints(end, 560, 46, 2.5, -1.05);
    const all = [...spiral, ...tail];
    return {
      sheaf: toPath(all),
      ink: toPath(jitter(spiral, 2.4)),
    };
  }, []);

  const lines = Array.from({ length: density }, (_, i) => i);
  const motionClass = motion === 'draw' ? 'ribbon-draw' : motion === 'loop' ? 'ribbon-loop' : '';

  return (
    <svg
      viewBox="0 0 900 900"
      fill="none"
      aria-hidden="true"
      focusable="false"
      className={`ribbon-art ${motionClass} ${className}`}
    >
      <defs>
        <linearGradient id={`rb-${gradientId}`} x1="180" y1="820" x2="880" y2="40" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#7fd8d0" />
          <stop offset="0.5" stopColor="#c9b8f0" />
          <stop offset="1" stopColor="#6b5ce7" />
        </linearGradient>
      </defs>

      <g stroke={`url(#rb-${gradientId})`} strokeLinecap="round" strokeLinejoin="round">
        {lines.map((i) => {
          const t = i / (density - 1);
          return (
            <path
              key={i}
              d={sheaf}
              pathLength={1}
              className="ribbon-line"
              strokeWidth={3 + Math.sin(t * Math.PI) * 5}
              strokeOpacity={0.12 + Math.sin(t * Math.PI) * 0.26}
              transform={`rotate(${(t - 0.5) * 12} 420 470) translate(${(t - 0.5) * 16} ${(t - 0.5) * -10})`}
              style={{ animationDelay: `${i * 40}ms` }}
            />
          );
        })}
      </g>

      {showInk && (
        <path
          d={ink}
          pathLength={1}
          className="ribbon-line"
          stroke="var(--color-ink)"
          strokeWidth={2.2}
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{ animationDelay: `${density * 40 + 300}ms`, animationDuration: '3.4s' }}
        />
      )}
    </svg>
  );
};
