import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';

export interface AccordionProps {
  id: string;
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
  className?: string;
}

export const Accordion: React.FC<AccordionProps> = ({
  id,
  title,
  children,
  defaultOpen = false,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className={`border border-slate-200 rounded-lg overflow-hidden bg-white ${className}`}>
      <button
        type="button"
        id={`header-${id}`}
        aria-expanded={isOpen}
        aria-controls={`panel-${id}`}
        onClick={() => setIsOpen((prev) => !prev)}
        className="w-full px-4 py-3.5 sm:px-5 sm:py-4 flex items-center justify-between text-left font-semibold text-slate-900 hover:bg-slate-50 transition-colors cursor-pointer"
      >
        <span className="text-sm sm:text-base leading-snug">{title}</span>
        <ChevronDown
          className={`w-4 h-4 text-slate-500 shrink-0 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
          aria-hidden="true"
        />
      </button>

      {isOpen && (
        <div
          id={`panel-${id}`}
          role="region"
          aria-labelledby={`header-${id}`}
          className="px-4 pb-4 sm:px-5 sm:pb-5 text-sm sm:text-base text-slate-600 leading-relaxed border-t border-slate-100 pt-3"
        >
          {children}
        </div>
      )}
    </div>
  );
};
