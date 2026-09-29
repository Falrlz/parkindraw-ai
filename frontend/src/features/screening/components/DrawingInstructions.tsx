import React from 'react';
import { Info } from 'lucide-react';
import type { StepInstructionContent } from '../../../content/types';
import { Medallion } from '../../../components/brand/Medallion';

export interface DrawingInstructionsProps {
  instruction: StepInstructionContent;
}

export const DrawingInstructions: React.FC<DrawingInstructionsProps> = ({ instruction }) => {
  return (
    <div className="text-ink">
      <Medallion
        pattern={instruction.modality}
        className="w-24 sm:w-28 short:w-16 tight:hidden text-ink mb-8 short:mb-4"
      />

      <h2 className="text-4xl sm:text-5xl short:text-4xl font-medium tracking-[-0.03em] leading-[1.05]">
        {instruction.title}
      </h2>

      <p className="mt-5 short:mt-3 text-lg sm:text-xl short:text-lg text-body leading-relaxed max-w-[48ch]">
        {instruction.instructionText}
      </p>

      <div className="mt-8 pt-5 short:mt-4 short:pt-3 border-t border-line flex items-start gap-3 text-base text-body leading-relaxed">
        <Info className="w-5 h-5 text-iris shrink-0 mt-0.5" strokeWidth={1.75} aria-hidden="true" />
        <span>
          <strong className="font-semibold text-ink">Tips:</strong> {instruction.canvasTip}
        </span>
      </div>
    </div>
  );
};
