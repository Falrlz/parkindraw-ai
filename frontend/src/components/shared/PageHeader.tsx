import React from 'react';

export interface PageHeaderProps {
  badge?: string;
  title: string;
  subtitle?: string;
  className?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  badge,
  title,
  subtitle,
  className = '',
}) => {
  return (
    <header className={`text-center max-w-3xl mx-auto mb-8 sm:mb-12 ${className}`}>
      {badge && (
        <p className="text-xs font-semibold tracking-wider uppercase text-teal-800 bg-teal-50 border border-teal-200 inline-block px-3 py-1 rounded-full mb-3">
          {badge}
        </p>
      )}
      <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900 leading-tight">
        {title}
      </h1>
      {subtitle && (
        <p className="mt-3 text-base sm:text-lg text-slate-600 leading-relaxed">
          {subtitle}
        </p>
      )}
    </header>
  );
};
