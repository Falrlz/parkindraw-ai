import type { NavigationContent } from './types';

export const navigationContent: NavigationContent = {
  brand: {
    title: 'Parkindraw',
    tagline: 'Clinical Screening',
  },
  menuItems: [
    {
      id: 'home',
      label: 'Beranda',
      path: '/',
    },
    {
      id: 'screening',
      label: 'Skrining',
      path: '/screening',
    },
    {
      id: 'about',
      label: 'Tentang',
      path: '/about',
    },
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
};
