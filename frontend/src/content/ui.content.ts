import type { Localized } from '../app/localeContext';
import type { UiContent } from './types';

/** Interface chrome: navbar controls, settings panel, and their accessible names. */
export const uiContent: Localized<UiContent> = {
  id: {
    settings: {
      title: 'Pengaturan',
      theme: 'Tema',
      themeOptions: { light: 'Terang', dark: 'Gelap', system: 'Sistem' },
      language: 'Bahasa',
    },
    nav: {
      mainLabel: 'Navigasi Utama',
      mobileLabel: 'Menu Navigasi Mobile',
      openMenu: 'Buka menu navigasi',
      closeMenu: 'Tutup menu navigasi',
    },
  },
  en: {
    settings: {
      title: 'Settings',
      theme: 'Theme',
      themeOptions: { light: 'Light', dark: 'Dark', system: 'System' },
      language: 'Language',
    },
    nav: {
      mainLabel: 'Main navigation',
      mobileLabel: 'Mobile navigation menu',
      openMenu: 'Open navigation menu',
      closeMenu: 'Close navigation menu',
    },
  },
};
