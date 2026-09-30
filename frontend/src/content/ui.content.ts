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
      skipToContent: 'Lewati ke Konten Utama',
    },
    common: {
      openInNewTab: '(membuka tab baru)',
    },
    backendStatus: {
      checking: 'Memeriksa Sistem...',
      online: 'Backend Online',
      offline: 'Backend Offline',
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
      skipToContent: 'Skip to main content',
    },
    common: {
      openInNewTab: '(opens in a new tab)',
    },
    backendStatus: {
      checking: 'Checking System...',
      online: 'Backend Online',
      offline: 'Backend Offline',
    },
  },
};
