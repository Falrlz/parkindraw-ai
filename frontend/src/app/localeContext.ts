import { createContext, useContext } from 'react';

export type Locale = 'id' | 'en';

/** Bahasa Indonesia is the primary language; English is the second. */
export const DEFAULT_LOCALE: Locale = 'id';
export const LOCALES: readonly Locale[] = ['id', 'en'];

export interface LocaleContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
}

export const LocaleContext = createContext<LocaleContextType>({
  locale: DEFAULT_LOCALE,
  setLocale: () => {},
});

export const useLocale = () => useContext(LocaleContext);

/**
 * Content written per language. English is optional while a surface is still
 * untranslated: a missing entry falls back to Bahasa Indonesia.
 */
export type Localized<T> = { id: T } & Partial<Record<Exclude<Locale, 'id'>, T>>;

export function pickLocale<T>(content: Localized<T>, locale: Locale): T {
  return content[locale] ?? content.id;
}

/** Reads the current language's version of a localized content object. */
export function useLocalized<T>(content: Localized<T>): T {
  const { locale } = useLocale();
  return pickLocale(content, locale);
}
