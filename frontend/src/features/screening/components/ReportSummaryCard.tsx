import React from 'react';
import { CheckCircle2, AlertTriangle } from 'lucide-react';
import type { SessionPredictionResponse, DrawingModality } from '../../../services/types';
import { useLocalized } from '../../../app/localeContext';
import { screeningContent } from '../../../content/screening.content';
import { useCountUp } from '../hooks/useCountUp';
import { ProbabilityScale } from './ProbabilityScale';

export interface ReportSummaryCardProps {
  result: SessionPredictionResponse;
}

/**
 * Report opening: the verdict set like a step title on the left, the one
 * measuring instrument on the right. No card, no accent stripe.
 */
export const ReportSummaryCard: React.FC<ReportSummaryCardProps> = ({ result }) => {
  const { report, steps } = useLocalized(screeningContent);
  const isParkinson = result.fusion_prediction === 'Parkinson';
  const percentage = result.fusion_probability * 100;
  const shown = useCountUp(percentage);

  const readings = (['circle', 'meander', 'spiral'] as DrawingModality[]).map((m) => ({
    modality: m,
    label: steps[m].title,
    value: result.drawings[m].probabilities.Parkinson,
  }));

  return (
    <section className="print-break-avoid grid grid-cols-12 gap-x-6 lg:gap-x-12 gap-y-10 pb-10 short:pb-8 border-b border-line">
      <div className="col-span-12 lg:col-span-5">
        {/* Item heading step (30 → 36px), one below the screen title */}
        <h3 className="text-3xl sm:text-4xl short:text-3xl font-medium tracking-[-0.03em] leading-[1.1] text-ink">
          {(isParkinson ? report.statusLabels.parkinson : report.statusLabels.healthy).replace(' / ', ' / ')}
        </h3>
        <p className={`mt-4 flex items-center gap-2 text-base font-medium ${isParkinson ? 'text-amber-ink' : 'text-aqua-deep'}`}>
          {isParkinson ? (
            <AlertTriangle className="w-4 h-4 shrink-0" strokeWidth={2} aria-hidden="true" />
          ) : (
            <CheckCircle2 className="w-4 h-4 shrink-0" strokeWidth={2} aria-hidden="true" />
          )}
          {report.finalVerdictLabel}
        </p>
        <p className="mt-4 text-lg text-body leading-relaxed max-w-[48ch]">
          {isParkinson ? report.statusLabels.parkinsonDesc : report.statusLabels.healthyDesc}
        </p>
      </div>

      <div className="col-span-12 lg:col-span-7">
        <p className="text-sm text-body">{report.probabilityLabel}</p>
        {/* Display numeral on the same step as the home workflow numerals (36 → 48px) */}
        <p className="mt-1 text-4xl sm:text-5xl short:text-4xl font-medium tracking-[-0.04em] leading-none text-ink tabular">
          <span aria-hidden="true">{shown.toFixed(1)}</span>
          <span className="sr-only">{percentage.toFixed(1)}</span>
          <span className="text-[0.45em] tracking-[-0.02em] align-top ml-1 text-body">%</span>
        </p>

        <ProbabilityScale
          className="mt-6 short:mt-4"
          fused={result.fusion_probability}
          threshold={result.threshold}
          readings={readings}
          caption={report.probabilityHeading}
          thresholdLabel={report.thresholdLabel}
        />
      </div>
    </section>
  );
};
