import React from 'react';

import { aboutContent } from '../../../content/about.content';
import { Chapter } from './Chapter';

const lede = 'text-lg sm:text-xl short:text-[17px] squat:text-base text-body leading-relaxed';

/** First chapter: part of the page's opening screen, together with the page title. */
export const TransferLearningChapter: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { aiRationale } = aboutContent;

  return (
    <Chapter heading={aiRationale.heading} subline="Deep Residual Learning & Frozen Backbone" className={className}>
      <p className={`${lede} max-w-[60ch]`}>{aiRationale.transferLearningText}</p>
    </Chapter>
  );
};

export const LateFusionChapter: React.FC = () => {
  const { aiRationale } = aboutContent;

  return (
    <Chapter heading={aiRationale.lateFusionHeading} subline="Penggabungan Probabilitas Independen">
      <p className={`${lede} max-w-[62ch]`}>{aiRationale.lateFusionText}</p>

      <figure className="mt-8 rounded-[10px] bg-ink-fill text-white px-6 py-10 sm:px-10 sm:py-12">
        <code className="tabular block font-sans text-center text-lg sm:text-xl lg:text-2xl font-medium tracking-[-0.01em] leading-relaxed text-balance">
          {aiRationale.formulaText}
        </code>
      </figure>
    </Chapter>
  );
};
