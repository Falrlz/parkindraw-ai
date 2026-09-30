import React from 'react';
import { Check } from 'lucide-react';
import { useLocalized } from '../../../app/localeContext';
import { screeningContent } from '../../../content/screening.content';
import type { ScreeningStep } from '../types';

export interface StepIndicatorProps {
  currentStep: ScreeningStep;
}

/** Three measured segments on one rule; the current one is drawn in violet. */
export const StepIndicator: React.FC<StepIndicatorProps> = ({ currentStep }) => {
  const { steps: stepContent, wizard } = useLocalized(screeningContent);

  const steps = [
    { step: 1, label: stepContent.circle.title },
    { step: 2, label: stepContent.meander.title },
    { step: 3, label: stepContent.spiral.title },
  ];

  return (
    <nav aria-label={wizard.progressLabel} className="w-full mb-10 sm:mb-12 short:mb-6 tight:mb-4">
      <ol className="grid grid-cols-3 gap-2 sm:gap-3">
        {steps.map(({ step, label }) => {
          const isCompleted = currentStep > step;
          const isCurrent = currentStep === step;

          return (
            <li key={step} aria-current={isCurrent ? 'step' : undefined}>
              <span
                className={`block h-1 rounded-full transition-colors duration-500 ${
                  isCompleted ? 'bg-ink' : isCurrent ? 'bg-iris' : 'bg-line'
                }`}
                aria-hidden="true"
              />
              <span className="mt-3 flex items-center gap-2">
                <span
                  className={`tabular w-6 h-6 shrink-0 rounded-full flex items-center justify-center text-xs font-semibold ${
                    isCompleted
                      ? 'bg-ink text-ground'
                      : isCurrent
                      ? 'bg-iris text-on-iris'
                      : 'border border-line-strong text-muted'
                  }`}
                  aria-hidden="true"
                >
                  {isCompleted ? <Check className="w-3.5 h-3.5" strokeWidth={2.5} /> : step}
                </span>
                <span
                  className={`text-sm sm:text-[15px] font-medium truncate ${
                    isCurrent ? 'text-ink' : isCompleted ? 'text-body' : 'text-muted'
                  }`}
                >
                  {label}
                </span>
              </span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
