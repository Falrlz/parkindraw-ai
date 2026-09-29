import React from 'react';

export interface ChapterProps {
  heading: string;
  subline?: string;
  children: React.ReactNode;
  className?: string;
}

/** Prospectus chapter: heading held in the left column, body in the right. */
export const Chapter: React.FC<ChapterProps> = ({ heading, subline, children, className = '' }) => {
  return (
    <section className={`grid grid-cols-12 gap-x-6 gap-y-8 py-14 sm:py-20 short:py-12 squat:py-8 border-t border-line ${className}`}>
      <div className="col-span-12 lg:col-span-4">
        <div className="lg:sticky lg:top-28">
          <h2 className="text-3xl sm:text-4xl short:text-3xl squat:text-2xl font-medium tracking-[-0.03em] leading-[1.1] text-ink max-w-[18ch]">
            {heading}
          </h2>
          {subline && <p className="mt-3 text-base text-muted">{subline}</p>}
        </div>
      </div>
      <div className="col-span-12 lg:col-span-8 min-w-0">{children}</div>
    </section>
  );
};
