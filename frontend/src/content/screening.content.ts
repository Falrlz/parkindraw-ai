import type { ScreeningContent } from './types';

export const screeningContent: ScreeningContent = {
  preparation: {
    title: 'Panduan Pelaksanaan Skrining',
    subtitle:
      'Persiapkan diri Anda agar proses pengambilan sampel goresan berlangsung tenang, alami, dan optimal.',
    guidelines: [
      'Duduklah dengan santai dan bertumpu nyaman di depan meja yang stabil.',
      'Gunakan tangan dominan yang biasa Anda gunakan untuk menulis atau menggambar sehari-hari.',
      'Goreskan garis dengan kecepatan alami. Jangan terburu-buru dan jangan memaksakan kecepatan.',
      'Anda dapat menggambar langsung pada layar perangkat atau menggambar di selembar kertas putih polos lalu mengunggah fotonya.',
      'Sesi ini terdiri dari 3 pola berturut-turut: Lingkaran (Circle), Meander (Gelombang), dan diakhiri dengan Spiral.',
    ],
    startButtonText: 'Mulai Skrining Mandiri',
  },
  steps: {
    circle: {
      stepNumber: 1,
      modality: 'circle',
      title: 'Lingkaran (Circle)',
      category: 'Langkah 1 dari 3: Pola Melingkar Tertutup',
      instructionText:
        'Tarik garis melingkar utuh searah atau berlawanan jarum jam. Usahakan kedua ujung garis bertemu membentuk satu lingkaran tertutup.',
      canvasTip:
        'Goreskan secara wajar dalam satu tarikan napas tanpa ragu atau berhenti berulang kali.',
    },
    meander: {
      stepNumber: 2,
      modality: 'meander',
      title: 'Meander (Gelombang Berkelok)',
      category: 'Langkah 2 dari 3: Pola Berulang Sinusoidal',
      instructionText:
        'Buat pola gelombang sinusoidal berkelok secara berkesinambungan dari kiri ke kanan tanpa mengangkat pena.',
      canvasTip:
        'Pertahankan ritme puncak dan lembah gelombang secara konstan dan mengalir.',
    },
    spiral: {
      stepNumber: 3,
      modality: 'spiral',
      title: 'Spiral (Pilin Archimedes)',
      category: 'Langkah 3 dari 3: Pola Melingkar Berkelanjutan',
      instructionText:
        'Mulailah dari titik pusat, lalu putar garis melingkar keluar secara bertahap menyerupai bentuk obat nyamuk.',
      canvasTip:
        'Jaga jarak antar putaran agar membesar secara berangsur-angsur tanpa terputus.',
    },
  },
  report: {
    title: 'Laporan Hasil Penapisan Skrining',
    statusLabels: {
      healthy: 'Pola Gerakan Normal / Rendah Risiko',
      healthyDesc:
        'Karakteristik goresan tangan Anda tidak memperlihatkan anomali mikromotorik yang signifikan berdasarkan model pembanding.',
      parkinson: 'Terindikasi Karakteristik Pola Parkinson',
      parkinsonDesc:
        'Ditemukan indikasi ketidakteraturan kelengkungan, mikrografia, atau fluktuasi goresan yang menyerupai karakteristik neuromotorik Parkinson.',
    },
    probabilityHeading: 'Estimasi Probabilitas Fusi (Late Multi-Modal Fusion)',
    breakdownHeading: 'Rincian Analisis Per Modalitas Gambar',
    disclaimerTitle: 'Peringatan Medis Resmi',
    disclaimerBody:
      'Laporan ini merupakan hasil analisis penapisan komputasional berbasis model computer vision dan bukan vonis diagnosis medis definitif. Hasil ini dimaksudkan sebagai instrumen edukasi dan penapisan awal untuk didiskusikan bersama dokter spesialis saraf (neurolog) jika Anda atau kerabat mengalami keluhan gangguan motorik.',
    actions: {
      printPdf: 'Cetak / Simpan Laporan (PDF)',
      restart: 'Lakukan Skrining Baru',
    },
  },
};
