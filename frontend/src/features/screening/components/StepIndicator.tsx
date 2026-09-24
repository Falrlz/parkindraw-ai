import React from 'react';
import { Check } from 'lucide-react';
import type { ScreeningStep } from '../types';

export interface StepIndicatorProps {
  currentStep: ScreeningStep;
}

const steps = [
  { step: 1, label: 'Lingkaran' },
  { step: 2, label: 'Meander' },
  { step: 3, label: 'Spiral' },
];

export const StepIndicator: React.FC<StepIndicatorProps> = ({ currentStep }) => {
  return (
    <nav aria-label="Progres Tahapan Skrining" className="w-full mb-6 sm:mb-8">
      <ol className="flex items-center justify-between max-w-lg mx-auto relative">
        {/* Background Track Line */}
        <div
          className="absolute top-4 left-6 right-6 h-0.5 bg-slate-200 -z-0"
          aria-hidden="true"
        />

        {steps.map(({ step, label }) => {
          const isCompleted = currentStep > step;
          const isCurrent = currentStep === step;

          return (
            <li key={step} className="flex flex-col items-center relative z-10">
              <div
                aria-current={isCurrent ? 'step' : undefined}
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
                  isCompleted
                    ? 'bg-teal-700 text-white'
                    : isCurrent
                    ? 'bg-teal-800 text-white ring-4 ring-teal-100'
                    : 'bg-white border-2 border-slate-300 text-slate-500'
                }`}
              >
                {isCompleted ? <Check className="w-4 h-4" /> : step}
              </div>
              <span
                className={`mt-2 text-xs font-medium ${
                  isCurrent ? 'text-teal-900 font-semibold' : 'text-slate-600'
                }`}
              >
                {label}
              </span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
