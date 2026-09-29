import React, { useMemo } from 'react';
import { newHandPdSpiralPoints, toPath } from './spiral';

export type MedallionPattern = 'circle' | 'meander' | 'spiral';

export interface MedallionProps {
  pattern: MedallionPattern;
  className?: string;
}

/**
 * Minimal pattern seal: one hairline ring framing the test pattern itself,
 * drawn in the NewHandPD form (circle, squared meander, Archimedean spiral).
 */
export const Medallion: React.FC<MedallionProps> = ({ pattern, className = '' }) => {
  const motif = useMemo(() => {
    if (pattern === 'circle') {
      return 'M100 42 a58 58 0 1 1 -0.1 0';
    }
    if (pattern === 'spiral') {
      return toPath(newHandPdSpiralPoints(103, 101, 0.17, 220));
    }
    // NewHandPD meander: a squared spiral entering from the lower-left stem
    return 'M55 144 V56 H145 V121 H77 V78 H123 V100.5 H101.5';
  }, [pattern]);

  return (
    <svg viewBox="0 0 200 200" fill="none" aria-hidden="true" focusable="false" className={className}>
      <circle cx="100" cy="100" r="94" stroke="currentColor" strokeOpacity="0.3" strokeWidth="1.5" />
      <path d={motif} stroke="var(--color-iris)" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};
