import React from 'react';
import { useLocale, useLocalized, type Locale } from '../../app/localeContext';
import { uiContent } from '../../content/ui.content';

/** Each language names itself in its own tongue, so a reader of either can find theirs. */
const options: { id: Locale; name: string }[] = [
  { id: 'id', name: 'Bahasa Indonesia' },
  { id: 'en', name: 'English' },
];

/** Two-way radio group in the theme-switch family: a ground well whose active option lifts to paper. */
export const LanguageSwitch: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { locale, setLocale } = useLocale();
  const ui = useLocalized(uiContent);

  const onKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (!['ArrowRight', 'ArrowLeft', 'ArrowDown', 'ArrowUp'].includes(e.key)) return;
    e.preventDefault();
    const index = options.findIndex((o) => o.id === locale);
    const delta = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : -1;
    const next = options[(index + delta + options.length) % options.length];
    setLocale(next.id);
    e.currentTarget.querySelector<HTMLButtonElement>(`[data-locale-option="${next.id}"]`)?.focus();
  };

  return (
    <div
      role="radiogroup"
      aria-label={ui.settings.language}
      onKeyDown={onKeyDown}
      className={`grid grid-cols-2 gap-1 p-1 bg-ground border border-line rounded-lg ${className}`}
    >
      {options.map((option) => {
        const isActive = locale === option.id;
        return (
          <button
            key={option.id}
            type="button"
            role="radio"
            aria-checked={isActive}
            lang={option.id}
            tabIndex={isActive ? 0 : -1}
            data-locale-option={option.id}
            onClick={() => setLocale(option.id)}
            className={`inline-flex items-center justify-center min-h-12 px-2 rounded-md text-sm font-medium transition-colors cursor-pointer ${isActive ? 'bg-paper text-ink shadow-[0_1px_3px_rgba(27,21,71,0.18)]' : 'text-body hover:text-ink'}`}
          >
            {option.name}
          </button>
        );
      })}
    </div>
  );
};
