import { useEffect, useState } from 'react';

function prefersReducedMotion(): boolean {
  return typeof window !== 'undefined' && Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches);
}

/** Counts from 0 to `target` once; lands instantly when reduced motion is requested. */
export function useCountUp(target: number, durationMs = 1400): number {
  const reduced = prefersReducedMotion();
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (reduced) return;
    let frame = 0;
    const start = performance.now();
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / durationMs);
      const eased = 1 - Math.pow(2, -10 * t);
      setValue(t === 1 ? target : target * eased);
      if (t < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, durationMs, reduced]);

  return reduced ? target : value;
}
