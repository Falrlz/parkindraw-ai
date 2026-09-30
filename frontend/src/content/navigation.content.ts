import type { Localized } from '../app/localeContext';
import type { NavigationContent } from './types';

export const navigationContent: Localized<NavigationContent> = {
  id: {
    brand: {
      title: 'Parkindraw',
      tagline: 'Draw. Analyze. Screen.',
    },
    menuItems: [
      { id: 'home', label: 'Beranda', path: '/' },
      { id: 'screening', label: 'Skrining', path: '/screening' },
      { id: 'about', label: 'Tentang', path: '/about' },
    ],
    footer: {
      brandDescription:
        'Parkindraw adalah platform skrining berbasis kecerdasan buatan yang menganalisis perubahan mikromotorik halus pada goresan tangan untuk mendukung deteksi dini risiko Parkinson.',
      navigationTitle: 'Navigasi',
      disclaimerTitle: 'Peringatan Medis',
      disclaimerText:
        'Hasil skrining ditujukan untuk mendukung deteksi dini risiko Parkinson, bukan sebagai pengganti diagnosis, saran, atau perawatan medis oleh tenaga kesehatan profesional.',
      copyrightText: '© 2026 Parkindraw',
    },
  },
  en: {
    brand: {
      title: 'Parkindraw',
      tagline: 'Draw. Analyze. Screen.',
    },
    menuItems: [
      { id: 'home', label: 'Home', path: '/' },
      { id: 'screening', label: 'Screening', path: '/screening' },
      { id: 'about', label: 'About', path: '/about' },
    ],
    footer: {
      brandDescription:
        'Parkindraw is an AI-assisted screening platform that analyses subtle micromotor changes in hand drawings to support early detection of Parkinson’s risk.',
      navigationTitle: 'Navigation',
      disclaimerTitle: 'Medical Disclaimer',
      disclaimerText:
        'Screening results are meant to support early detection of Parkinson’s risk. They do not replace diagnosis, advice, or treatment from a qualified healthcare professional.',
      copyrightText: '© 2026 Parkindraw',
    },
  },
};
