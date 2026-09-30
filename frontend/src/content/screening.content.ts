import type { Localized } from '../app/localeContext';
import type { ScreeningContent } from './types';

export const screeningContent: Localized<ScreeningContent> = {
  id: {
    pageTitle: 'Sesi Penapisan Neuromotorik',
    preparation: {
      title: 'Panduan Pelaksanaan Skrining',
      subtitle:
        'Persiapkan diri Anda agar proses pengambilan sampel goresan berlangsung tenang, alami, dan optimal.',
      guidelines: [
        'Duduklah dengan santai dan bertumpu nyaman di depan meja yang stabil.',
        'Gunakan tangan dominan yang biasa Anda gunakan untuk menulis atau menggambar sehari-hari.',
        'Goreskan garis dengan kecepatan alami. Jangan terburu-buru dan jangan memaksakan kecepatan.',
        'Anda dapat menggambar langsung pada layar perangkat atau menggambar di selembar kertas putih polos lalu mengunggah fotonya.',
        'Sesi ini terdiri dari 3 pola berturut-turut: Lingkaran (Circle), Berkelok, dan diakhiri dengan Spiral.',
      ],
      startButtonText: 'Mulai Skrining Mandiri',
      instructionsLabel: 'Instruksi Persiapan',
    },
    steps: {
      circle: {
        stepNumber: 1,
        modality: 'circle',
        title: 'Lingkaran',
        category: 'Langkah 1 dari 3: Pola Melingkar Tertutup',
        instructionText:
          'Tarik garis melingkar utuh searah atau berlawanan jarum jam. Usahakan kedua ujung garis bertemu membentuk satu lingkaran tertutup.',
        canvasTip:
          'Goreskan secara wajar dalam satu tarikan napas tanpa ragu atau berhenti berulang kali.',
        tipsLabel: 'Tips:',
      },
      meander: {
        stepNumber: 2,
        modality: 'meander',
        title: 'Berkelok',
        category: 'Langkah 2 dari 3: Pola Siku Berkelok ke Dalam',
        instructionText:
          'Mulailah dari ujung kiri bawah, tarik garis lurus ke atas, lalu belok siku mengikuti panduan: ke kanan, ke bawah, ke kiri, dan terus masuk ke tengah tanpa mengangkat pena.',
        canvasTip:
          'Jaga garis tetap lurus, sudut belokan tetap tegas, dan jarak antar lintasan tetap sama.',
        tipsLabel: 'Tips:',
      },
      spiral: {
        stepNumber: 3,
        modality: 'spiral',
        title: 'Spiral',
        category: 'Langkah 3 dari 3: Pola Melingkar Berkelanjutan',
        instructionText:
          'Mulailah dari titik pusat, lalu putar garis melingkar keluar secara bertahap menyerupai bentuk obat nyamuk.',
        canvasTip:
          'Jaga jarak antar putaran agar membesar secara berangsur-angsur tanpa terputus.',
        tipsLabel: 'Tips:',
      },
    },
    wizard: {
      progressLabel: 'Progres Tahapan Skrining',
      navigationLabel: 'Navigasi Tahapan',
      inputModes: {
        canvas: 'Kanvas Digital',
        upload: 'Unggah Foto Kertas',
      },
      backButton: 'Kembali',
      nextPatternButton: 'Lanjut ke Pola Berikutnya',
      submitButton: 'Kirim & Analisis Seluruh Gambar',
      validation: {
        drawRequired: 'Harap buat goresan pada kanvas sebelum melanjutkan ke tahap berikutnya.',
        fileRequired: 'Harap pilih berkas foto gambar terlebih dahulu.',
        allStepsRequired: 'Harap selesaikan ketiga pola gambar (Lingkaran, Berkelok, dan Spiral) terlebih dahulu.',
        analysisFailed: 'Gagal menganalisis sesi skrining. Pastikan backend aktif dan coba lagi.',
        alertTitle: 'Perhatian',
      },
    },
    loading: {
      title: 'Memproses Analisis Pola Goresan',
      subtitle:
        'Model Computer Vision ResNet-18 sedang mengevaluasi keteraturan mikromotorik dari ketiga gambar dan menghitung Late Multi-Modal Fusion...',
      srText: 'Sedang memproses... Harap tunggu beberapa detik.',
    },
    canvas: {
      canvasAriaLabel: 'Kanvas gambar untuk pola',
      strokeLabel: 'Ketebalan',
      strokeOptions: {
        thin: 'Tipis',
        medium: 'Sedang',
        thick: 'Tebal',
      },
      showGuide: 'Lihat Panduan',
      hideGuide: 'Sembunyikan Panduan',
      undo: 'Urungkan',
      clear: 'Hapus',
    },
    upload: {
      dropzoneTitle: 'Klik untuk memilih foto atau seret berkas ke sini',
      dropzoneDesc:
        'Foto hasil gambar pada kertas putih polos. Format yang didukung: PNG, JPG, atau WebP (maks. 10 MB).',
      chooseFileButton: 'Pilih Foto Kertas',
      changeFileButton: 'Ganti Berkas',
      fileReadyText: 'Berkas siap diproses',
      previewAlt: 'Pratinjau berkas yang diunggah',
      invalidType: 'Format berkas tidak didukung. Harap pilih gambar PNG, JPG, atau WebP.',
      fileTooLarge: 'Ukuran berkas terlalu besar (maksimal 10 MB).',
    },
    report: {
      title: 'Laporan Skrining Pola Parkinson',
      subtitle: 'Hasil Evaluasi Karakteristik Goresan',
      metaLabels: {
        sessionId: 'ID Sesi',
        completedAt: 'Waktu Selesai',
      },
      statusLabels: {
        healthy: 'Pola Gerakan Normal',
        healthyShort: 'Rendah Risiko',
        healthyDesc:
          'Karakteristik goresan tangan Anda tidak memperlihatkan anomali mikromotorik yang signifikan berdasarkan model pembanding.',
        parkinson: 'Terindikasi Pola Parkinson',
        parkinsonShort: 'Terindikasi',
        parkinsonDesc:
          'Ditemukan indikasi ketidakteraturan kelengkungan, mikrografia, atau fluktuasi goresan yang menyerupai karakteristik neuromotorik Parkinson.',
      },
      finalVerdictLabel: 'Hasil Penapisan Akhir',
      probabilityLabel: 'Probabilitas Parkinson:',
      probabilityHeading: 'Estimasi Probabilitas Fusi (Late Multi-Modal Fusion)',
      thresholdLabel: 'Ambang Batas',
      breakdownHeading: 'Rincian Analisis Per Modalitas Gambar',
      scoreLabel: 'Skor Probabilitas Parkinson',
      noImageText: 'Tidak ada gambar',
      disclaimerTitle: 'Peringatan Medis Resmi',
      disclaimerBody:
        'Laporan ini merupakan hasil analisis penapisan komputasional berbasis model computer vision dan bukan vonis diagnosis medis definitif. Hasil ini dimaksudkan sebagai instrumen edukasi dan penapisan awal untuk didiskusikan bersama dokter spesialis saraf (neurolog) jika Anda atau kerabat mengalami keluhan gangguan motorik.',
      followUpNotice:
        'Langkah Lanjutan: Konsultasikan hasil pemeriksaan ini ke dokter spesialis saraf (neurolog) di fasilitas kesehatan terdekat untuk mendapatkan pemeriksaan klinis komprehensif.',
      actions: {
        printPdf: 'Cetak / Simpan Laporan (PDF)',
        restart: 'Lakukan Skrining Baru',
      },
    },
  },
};
