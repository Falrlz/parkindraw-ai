import React from 'react';
import { Monitor, Moon, Sun } from 'lucide-react';
import { useTheme, type ThemePreference } from '../../app/themeContext';

const options: { id: ThemePreference; label: string; icon: React.ReactNode }[] = [
  { id: 'light', label: 'Terang', icon: <Sun className="w-4 h-4" strokeWidth={1.75} aria-hidden="true" /> },
  { id: 'dark', label: 'Gelap', icon: <Moon className="w-4 h-4" strokeWidth={1.75} aria-hidden="true" /> },
  { id: 'system', label: 'Sistem', icon: <Monitor className="w-4 h-4" strokeWidth={1.75} aria-hidden="true" /> },
];

/** Three-way segmented radio group: light, dark, follow the operating system. */
export const ThemeSwitch: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { preference, setPreference } = useTheme();

  const onKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (!['ArrowRight', 'ArrowLeft', 'ArrowDown', 'ArrowUp'].includes(e.key)) return;
    e.preventDefault();
    const index = options.findIndex((o) => o.id === preference);
    const delta = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : -1;
    const next = options[(index + delta + options.length) % options.length];
    setPreference(next.id);
    e.currentTarget.querySelector<HTMLButtonElement>(`[data-theme-option="${next.id}"]`)?.focus();
  };

  return (
    <div
      role="radiogroup"
      aria-label="Tema"
      onKeyDown={onKeyDown}
      className={`grid grid-cols-3 gap-1 p-1 bg-ground border border-line rounded-lg ${className}`}
    >
      {options.map((option) => {
        const isActive = preference === option.id;
        return (
          <button
            key={option.id}
            type="button"
            role="radio"
            aria-checked={isActive}
            tabIndex={isActive ? 0 : -1}
            data-theme-option={option.id}
            onClick={() => setPreference(option.id)}
            className={`inline-flex flex-col items-center justify-center gap-1 min-h-14 px-2 rounded-md text-sm font-medium transition-colors cursor-pointer ${
              isActive ? 'bg-paper text-ink shadow-[0_1px_3px_rgba(27,21,71,0.18)]' : 'text-body hover:text-ink'
            }`}
          >
            {option.icon}
            {option.label}
          </button>
        );
      })}
    </div>
  );
};
