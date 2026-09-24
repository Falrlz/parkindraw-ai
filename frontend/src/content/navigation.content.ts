import type { NavigationContent } from './types';

export const navigationContent: NavigationContent = {
  brand: {
    title: 'ParkinDraw AI',
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
      isAction: true,
    },
    {
      id: 'about',
      label: 'Tentang',
      path: '/about',
    },
    {
      id: 'faq',
      label: 'FAQ',
      path: '/faq',
    },
  ],
  footer: {
    brandDescription:
      'ParkinDraw adalah platform penapisan dini berbasis kecerdasan buatan (computer vision) yang menganalisis perubahan mikromotorik halus pada goresan tangan. Dirancang sebagai instrumen skrining awal yang cepat, non-invasif, dan objektif untuk membantu deteksi dini tremor dan ketidakteraturan motorik terkait Penyakit Parkinson.',
    navigationTitle: 'Navigasi',
    disclaimerTitle: 'Peringatan Medis',
    disclaimerText:
      'ParkinDraw dirancang secara eksklusif sebagai alat bantu penapisan awal (screening research tool) dan bukan instrumen diagnosis medis definitif. Hasil analisis probabilitas sistem ini tidak menggantikan pemeriksaan fisik, anamnesis, maupun evaluasi klinis resmi oleh dokter spesialis saraf (neurolog). Jika Anda atau kerabat mengalami gejala gangguan gerak, segera konsultasikan ke fasilitas pelayanan kesehatan terdekat.',
    copyrightText: '© 2026 ParkinDraw AI • Computer-Assisted Parkinson\'s Disease Screening Research',
  },
};
