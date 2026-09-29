import React, { useEffect, useId, useRef, useState } from 'react';
import { Settings } from 'lucide-react';
import { ThemeSwitch } from './ThemeSwitch';

/** Navbar settings: a gear that opens a small panel anchored to the right edge. */
export const SettingsMenu: React.FC = () => {
  const [open, setOpen] = useState(false);
  const panelId = useId();
  const rootRef = useRef<HTMLDivElement | null>(null);
  const buttonRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    if (!open) return;
    const onPointer = (e: PointerEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setOpen(false);
        buttonRef.current?.focus();
      }
    };
    document.addEventListener('pointerdown', onPointer);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('pointerdown', onPointer);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  return (
    <div ref={rootRef} className="relative">
      <button
        ref={buttonRef}
        type="button"
        aria-label="Pengaturan"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((prev) => !prev)}
        className={`w-11 h-11 flex items-center justify-center rounded-md transition-colors cursor-pointer ${
          open ? 'bg-iris-wash text-iris' : 'text-ink hover:bg-iris-wash hover:text-iris'
        }`}
      >
        <Settings
          className={`w-5 h-5 transition-transform duration-500 ease-out ${open ? 'rotate-90' : ''}`}
          strokeWidth={1.75}
          aria-hidden="true"
        />
      </button>

      {open && (
        <div
          id={panelId}
          role="group"
          aria-label="Pengaturan"
          className="absolute right-0 top-full mt-2 w-64 p-4 bg-paper border border-line rounded-[10px] shadow-[0_12px_32px_-12px_rgba(15,14,26,0.35)] z-50"
        >
          <p className="text-base font-semibold text-ink">Pengaturan</p>
          <p className="mt-3 mb-2 text-sm text-muted">Tema</p>
          <ThemeSwitch />
        </div>
      )}
    </div>
  );
};
