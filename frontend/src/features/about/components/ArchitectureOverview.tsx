import React from 'react';

import { useLocalized } from '../../../app/localeContext';
import { aboutContent } from '../../../content/about.content';
import { Chapter } from './Chapter';

const lede = 'text-lg sm:text-xl short:text-[17px] squat:text-base text-body leading-relaxed';

/** First chapter: part of the page's opening screen, together with the page title. */
export const TransferLearningChapter: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { aiRationale } = useLocalized(aboutContent);

  return (
    <Chapter heading={aiRationale.heading} subline={aiRationale.transferLearningSubline} className={className}>
      <p className={`${lede} max-w-[60ch]`}>{aiRationale.transferLearningText}</p>
    </Chapter>
  );
};

export const LateFusionChapter: React.FC = () => {
  const { aiRationale } = useLocalized(aboutContent);

  return (
    <Chapter heading={aiRationale.lateFusionHeading} subline={aiRationale.lateFusionSubline}>
      <p className={`${lede} max-w-[62ch]`}>{aiRationale.lateFusionText}</p>

      <figure className="mt-8 rounded-[10px] bg-ink-fill text-white px-3 sm:px-10 py-6 sm:py-10">
        <div
          role="img"
          aria-label="P_fusion(Parkinson) = [ P(Circle) + P(Meander) + P(Spiral) ] / 3"
          className="w-full overflow-x-auto py-2 select-none"
        >
          <div className="w-max min-w-full flex items-center justify-center px-2">
            <div className="inline-flex items-center gap-1.5 sm:gap-3 lg:gap-4 text-xs sm:text-base lg:text-xl font-normal tracking-wide">
              {/* Sisi Kiri: P_fusion(Parkinson) */}
              <div className="flex items-baseline">
                <span className="font-serif italic text-lg sm:text-2xl lg:text-3xl text-on-ink-accent font-medium">P</span>
                <sub className="text-[10px] sm:text-xs font-sans text-lilac ml-0.5 mr-0.5 sm:mr-1 font-normal">fusion</sub>
                <span className="font-sans text-white/95 text-xs sm:text-base lg:text-lg font-medium">(Parkinson)</span>
              </div>

              {/* Simbol Sama Dengan */}
              <span className="text-sm sm:text-xl lg:text-2xl font-light text-lilac mx-0.5 sm:mx-1">=</span>

              {/* Sisi Kanan: Pecahan (Fraction) */}
              <div className="inline-flex flex-col items-center">
                {/* Pembilang (Numerator) */}
                <div className="px-1.5 sm:px-4 pb-1 sm:pb-2 text-center flex items-baseline gap-1 sm:gap-2.5 flex-nowrap whitespace-nowrap">
                  <span className="inline-flex items-baseline">
                    <span className="font-serif italic text-base sm:text-xl lg:text-2xl text-on-ink-accent font-medium">P</span>
                    <span className="font-sans text-white/95 text-[11px] sm:text-sm lg:text-base font-medium">(Circle)</span>
                  </span>
                  <span className="text-lilac font-light text-xs sm:text-base">+</span>
                  <span className="inline-flex items-baseline">
                    <span className="font-serif italic text-base sm:text-xl lg:text-2xl text-on-ink-accent font-medium">P</span>
                    <span className="font-sans text-white/95 text-[11px] sm:text-sm lg:text-base font-medium">(Meander)</span>
                  </span>
                  <span className="text-lilac font-light text-xs sm:text-base">+</span>
                  <span className="inline-flex items-baseline">
                    <span className="font-serif italic text-base sm:text-xl lg:text-2xl text-on-ink-accent font-medium">P</span>
                    <span className="font-sans text-white/95 text-[11px] sm:text-sm lg:text-base font-medium">(Spiral)</span>
                  </span>
                </div>

                {/* Garis Pecahan (Fraction Bar) */}
                <div className="w-full h-[1.5px] bg-white/40 rounded-full" />

                {/* Penyebut (Denominator) */}
                <div className="pt-1 sm:pt-2 text-center font-serif text-sm sm:text-xl lg:text-2xl text-white font-medium">
                  3
                </div>
              </div>
            </div>
          </div>
        </div>
      </figure>
    </Chapter>
  );
};
