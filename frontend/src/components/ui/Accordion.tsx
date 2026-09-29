import React, { useState } from 'react';
import { Plus } from 'lucide-react';

export interface AccordionProps {
  id: string;
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
  className?: string;
}

/** Register-style disclosure: hairline rows, no boxes. */
export const Accordion: React.FC<AccordionProps> = ({
  id,
  title,
  children,
  defaultOpen = false,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className={`border-b border-line ${className}`}>
      <h3>
        <button
          type="button"
          id={`header-${id}`}
          aria-expanded={isOpen}
          aria-controls={`panel-${id}`}
          onClick={() => setIsOpen((prev) => !prev)}
          className="group w-full py-5 sm:py-6 flex items-start justify-between gap-6 text-left cursor-pointer"
        >
          <span
            className={`text-lg sm:text-xl font-medium leading-snug tracking-[-0.01em] transition-colors ${
              isOpen ? 'text-iris' : 'text-ink group-hover:text-iris'
            }`}
          >
            {title}
          </span>
          <span
            className={`mt-0.5 w-8 h-8 shrink-0 rounded-full border flex items-center justify-center transition-[transform,background-color,border-color,color] duration-300 ease-out ${
              isOpen
                ? 'rotate-45 bg-iris border-iris text-on-iris'
                : 'border-line-strong text-ink group-hover:border-iris group-hover:text-iris'
            }`}
            aria-hidden="true"
          >
            <Plus className="w-4 h-4" strokeWidth={1.75} />
          </span>
        </button>
      </h3>

      <div
        id={`panel-${id}`}
        role="region"
        aria-labelledby={`header-${id}`}
        hidden={!isOpen}
        className="pb-6 pr-12 text-base text-body leading-relaxed"
      >
        {children}
      </div>
    </div>
  );
};
