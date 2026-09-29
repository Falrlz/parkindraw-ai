import React from 'react';

export interface PageHeaderProps {
  badge?: string;
  title: string;
  subtitle?: string;
  className?: string;
  /** Optional art set to the right of the heading on wide screens. */
  aside?: React.ReactNode;
}

/**
 * Prospectus page opening: left-set display heading and lede; the page's
 * label is document meta inside the title block, closed by the hairline.
 */
export const PageHeader: React.FC<PageHeaderProps> = ({
  badge,
  title,
  subtitle,
  className = '',
  aside,
}) => {
  return (
    <header className={`relative mb-12 sm:mb-16 pb-10 sm:pb-12 short:mb-8 short:pb-6 squat:pb-4 border-b border-line ${className}`}>
      <div className="grid grid-cols-12 gap-x-6 items-end">
        <div className="col-span-12 lg:col-span-8">
          <h1 className="text-[40px] sm:text-6xl lg:text-[72px] short:text-[52px] squat:text-[44px] font-medium tracking-[-0.035em] leading-[1.02] text-ink">
            {title}
          </h1>
          {subtitle && (
            <p className="mt-6 short:mt-4 max-w-[60ch] text-lg sm:text-xl short:text-lg squat:text-base text-body leading-relaxed">
              {subtitle}
            </p>
          )}
          {badge && <p className="mt-6 short:mt-3 text-sm text-muted">{badge}</p>}
        </div>
        {aside && <div className="hidden lg:block col-span-4">{aside}</div>}
      </div>
    </header>
  );
};
