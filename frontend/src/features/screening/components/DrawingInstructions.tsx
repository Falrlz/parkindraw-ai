import React from 'react';
import { Info } from 'lucide-react';
import type { StepInstructionContent } from '../../../content/types';

export interface DrawingInstructionsProps {
  instruction: StepInstructionContent;
}

export const DrawingInstructions: React.FC<DrawingInstructionsProps> = ({ instruction }) => {
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 sm:p-5 mb-5 text-slate-800">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-2">
        <p className="text-xs font-bold uppercase tracking-wider text-teal-800">
          {instruction.category}
        </p>
        <span className="text-xs text-slate-500 font-medium">
          Format: Citra Kanvas Kontras Tinggi
        </span>
      </div>

      <h2 className="text-xl sm:text-2xl font-bold text-slate-900 mb-2">
        {instruction.title}
      </h2>

      <p className="text-sm sm:text-base text-slate-700 leading-relaxed mb-3">
        {instruction.instructionText}
      </p>

      <div className="flex items-start gap-2 text-xs text-slate-600 bg-white p-2.5 rounded-lg border border-slate-200">
        <Info className="w-4 h-4 text-teal-700 shrink-0 mt-0.5" aria-hidden="true" />
        <span><strong>Tips:</strong> {instruction.canvasTip}</span>
      </div>
    </div>
  );
};
