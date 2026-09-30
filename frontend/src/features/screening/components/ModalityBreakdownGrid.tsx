import React from 'react';
import type { SessionPredictionResponse, DrawingModality } from '../../../services/types';
import { useLocalized } from '../../../app/localeContext';
import { screeningContent } from '../../../content/screening.content';
import { Medallion } from '../../../components/brand/Medallion';

export interface ModalityBreakdownGridProps {
  result: SessionPredictionResponse;
  thumbnails: Record<DrawingModality, string | null>;
}

/**
 * The three specimens as a register, the same grammar as "Tiga Pola" on the
 * home page: seal and name, the person's own drawing on its sheet, the reading.
 */
export const ModalityBreakdownGrid: React.FC<ModalityBreakdownGridProps> = ({
  result,
  thumbnails,
}) => {
  const { report, steps } = useLocalized(screeningContent);
  const modalities: DrawingModality[] = ['circle', 'meander', 'spiral'];

  return (
    <section className="pt-10 short:pt-8">
      <h3 className="text-3xl sm:text-4xl short:text-3xl font-medium tracking-[-0.03em] leading-[1.1] text-ink">
        {report.breakdownHeading}
      </h3>

      <ul className="mt-6 border-t border-ink/80">
        {modalities.map((modality) => {
          const prediction = result.drawings[modality];
          const meta = steps[modality];
          const isParkinson = prediction.prediction === 'Parkinson';
          const parkinsonProb = prediction.probabilities.Parkinson * 100;
          const thumbnail = thumbnails[modality];

          return (
            <li
              key={modality}
              className="print-break-avoid grid grid-cols-12 items-center gap-x-4 sm:gap-x-6 py-5 border-b border-line"
            >
              {/* Seal, name, and verdict for this pattern */}
              <div className="col-span-12 sm:col-span-6 flex items-start gap-4">
                <Medallion pattern={modality} className="w-11 h-11 sm:w-12 sm:h-12 shrink-0 text-ink" />
                <div className="min-w-0">
                  <h4 className="text-2xl font-medium tracking-[-0.02em] text-ink">{meta.title}</h4>
                  <p className="text-sm text-muted">{meta.category}</p>
                  <p
                    className={`mt-2 flex items-center gap-2 text-sm font-medium ${
                      isParkinson ? 'text-amber-ink' : 'text-aqua-deep'
                    }`}
                  >
                    <span
                      className={`w-2 h-2 rounded-full shrink-0 ${isParkinson ? 'bg-amber-rule' : 'bg-aqua-rule'}`}
                      aria-hidden="true"
                    />
                    {isParkinson ? report.statusLabels.parkinsonShort : report.statusLabels.healthyShort}
                  </p>
                </div>
              </div>

              {/* The person's own drawing, on a single sheet like the canvas */}
              <div className="col-span-5 sm:col-span-3 mt-4 sm:mt-0 pl-[60px] sm:pl-0">
                <div className="w-20 sm:w-24 aspect-square bg-white border border-line-strong rounded-md overflow-hidden flex items-center justify-center">
                  {thumbnail ? (
                    <img src={thumbnail} alt={meta.title} className="max-w-full max-h-full object-contain" />
                  ) : (
                    <span className="text-xs text-muted text-center px-1">{report.noImageText}</span>
                  )}
                </div>
              </div>

              <div className="col-span-7 sm:col-span-3 mt-4 sm:mt-0 text-right">
                <p className="text-sm text-muted">{report.scoreLabel}</p>
                <p className="text-2xl sm:text-3xl font-medium tracking-[-0.03em] text-ink tabular">
                  {parkinsonProb.toFixed(1)}%
                </p>
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
};
