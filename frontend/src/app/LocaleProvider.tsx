import React, { useCallback, useEffect, useState } from 'react';
import { DEFAULT_LOCALE, LocaleContext, LOCALES, type Locale } from './localeContext';

const STORAGE_KEY = 'parkindraw-locale';

function readLocale(): Locale {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored && (LOCALES as readonly string[]).includes(stored)) return stored as Locale;
  } catch {
    // storage blocked (private mode, disabled site data): use the primary language
  }
  return DEFAULT_LOCALE;
}

export const LocaleProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [locale, setLocaleState] = useState<Locale>(readLocale);

  // Keep <html lang> truthful so screen readers, hyphenation and translators follow the UI
  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // not persisted; the choice still applies for this visit
    }
  }, []);

  return <LocaleContext.Provider value={{ locale, setLocale }}>{children}</LocaleContext.Provider>;
};
