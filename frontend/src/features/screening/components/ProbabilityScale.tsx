import React from 'react';
import type { DrawingModality } from '../../../services/types';
import { Medallion } from '../../../components/brand/Medallion';

export interface ScaleReading {
  modality: DrawingModality;
  label: string;
  value: number; // 0..1
}

export interface ProbabilityScaleProps {
  fused: number; // 0..1
  threshold: number; // 0..1
  readings: ScaleReading[];
  caption: string;
  thresholdLabel?: string;
  className?: string;
}

const pct = (v: number) => Math.min(100, Math.max(0, v * 100));
/** Keep edge labels inside the ruler. */
const clampLabel = (p: number) => Math.min(94, Math.max(6, p));

/**
 * One measuring instrument for the whole session: a hairline ruler from 0 to
 * 100%, the decision threshold drawn on it, the fused estimate marked below,
 * and each pattern's reading pinned above by its seal on a leader line.
 * Built from borders and SVG strokes only, so it survives printing.
 */
export const ProbabilityScale: React.FC<ProbabilityScaleProps> = ({
  fused,
  threshold,
  readings,
  caption,
  thresholdLabel = 'Ambang Batas',
  className = '',
}) => {
  const fusedPct = pct(fused);
  const thresholdPct = pct(threshold);

  // Two lanes above the ruler so seals with close readings never overlap
  const placed = [...readings]
    .sort((a, b) => a.value - b.value)
    .reduce<(ScaleReading & { lane: 0 | 1 })[]>((acc, r) => {
      const prevSameLane = [...acc].reverse().find((p) => p.lane === 0);
      const crowded = prevSameLane && pct(r.value) - pct(prevSameLane.value) < 9;
      acc.push({ ...r, lane: crowded ? 1 : 0 });
      return acc;
    }, []);

  const BASE = 112; // y of the ruler line, px

  return (
    <figure className={`print-break-avoid ${className}`}>
      <div
        role="img"
        aria-label={`${caption}: ${fusedPct.toFixed(1)}%. ${thresholdLabel}: ${thresholdPct.toFixed(0)}%. ${readings
          .map((r) => `${r.label}: ${pct(r.value).toFixed(1)}%`)
          .join('. ')}.`}
        className="relative h-[168px] mx-4 sm:mx-5"
      >
        {/* Threshold: dashed rule with its label on top */}
        <span
          className="absolute top-5 border-l border-dashed border-ink/50"
          style={{ left: `${thresholdPct}%`, height: BASE - 20 + 12 }}
          aria-hidden="true"
        />
        <span
          className="absolute top-0 -translate-x-1/2 whitespace-nowrap text-xs font-medium text-body"
          style={{ left: `${clampLabel(thresholdPct)}%` }}
          aria-hidden="true"
        >
          {thresholdLabel}: {thresholdPct.toFixed(0)}%
        </span>

        {/* Pattern readings: seal on a leader line */}
        {placed.map((r) => {
          const top = r.lane === 1 ? 24 : 60;
          return (
            <span
              key={r.modality}
              className="absolute -translate-x-1/2 flex flex-col items-center"
              style={{ left: `${pct(r.value)}%`, top }}
              aria-hidden="true"
            >
              <Medallion pattern={r.modality} className="w-8 h-8 text-ink bg-ground rounded-full" />
              <span className="border-l border-ink/40" style={{ height: BASE - top - 32 }} />
            </span>
          );
        })}

        {/* The ruler: baseline plus decile ticks */}
        <span className="absolute left-0 right-0 border-t-2 border-ink" style={{ top: BASE }} aria-hidden="true" />
        {Array.from({ length: 11 }, (_, i) => (
          <span
            key={i}
            className={`absolute border-l border-ink/50 ${i % 5 === 0 ? 'h-3' : 'h-1.5'}`}
            style={{ left: `${i * 10}%`, top: BASE + 2 }}
            aria-hidden="true"
          />
        ))}
        <span className="absolute left-0 -translate-x-1/2 text-xs text-muted tabular" style={{ top: BASE + 20 }} aria-hidden="true">
          0%
        </span>
        <span className="absolute left-full -translate-x-1/2 text-xs text-muted tabular" style={{ top: BASE + 20 }} aria-hidden="true">
          100%
        </span>

        {/* Fused estimate: ink pointer under the ruler with its value */}
        <span
          className="absolute -translate-x-1/2 flex flex-col items-center"
          style={{ left: `${fusedPct}%`, top: BASE + 4 }}
          aria-hidden="true"
        >
          <svg viewBox="0 0 16 12" className="w-4 h-3 text-ink">
            <path d="M8 0 L16 12 H0 Z" fill="currentColor" />
          </svg>
        </span>
        <span
          className="absolute -translate-x-1/2 whitespace-nowrap text-base font-semibold text-ink tabular"
          style={{ left: `${clampLabel(fusedPct)}%`, top: BASE + 20 }}
          aria-hidden="true"
        >
          {fusedPct.toFixed(1)}%
        </span>
      </div>
      <figcaption className="mt-2 text-sm text-muted">{caption}</figcaption>
    </figure>
  );
};
