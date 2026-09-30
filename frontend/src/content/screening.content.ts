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
      disclaimerTitle: 'Peringatan Medis',
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
  en: {
    pageTitle: 'Neuromotor Screening Session',
    preparation: {
      title: 'Screening Session Guidelines',
      subtitle:
        'Prepare yourself so that the drawing assessment process is calm, natural, and optimal.',
      guidelines: [
        'Sit comfortably and relaxed at a stable table or desk.',
        'Use your dominant hand, the one you normally write or draw with.',
        'Draw at your natural speed. Do not rush or force unnatural speed.',
        'You can draw directly on the screen or draw on plain white paper and upload a photo.',
        'This session consists of 3 consecutive patterns: Circle, Meander, and ending with Spiral.',
      ],
      startButtonText: 'Start Self-Screening',
      instructionsLabel: 'Preparation Instructions',
    },
    steps: {
      circle: {
        stepNumber: 1,
        modality: 'circle',
        title: 'Circle',
        category: 'Step 1 of 3: Closed Circular Loop Pattern',
        instructionText:
          'Draw a full continuous circle clockwise or counter-clockwise. Try to meet both endpoints to form a closed loop.',
        canvasTip:
          'Draw naturally in one single continuous motion without hesitating or repeatedly pausing.',
        tipsLabel: 'Tips:',
      },
      meander: {
        stepNumber: 2,
        modality: 'meander',
        title: 'Meander',
        category: 'Step 2 of 3: Inward Right-Angled Meander Pattern',
        instructionText:
          'Start from the bottom-left corner, draw straight up, then make perpendicular turns following the guide: right, down, left, and inward toward the center without lifting the pen.',
        canvasTip:
          'Keep lines straight, turns sharp and perpendicular, and maintain consistent lane spacing.',
        tipsLabel: 'Tips:',
      },
      spiral: {
        stepNumber: 3,
        modality: 'spiral',
        title: 'Spiral',
        category: 'Step 3 of 3: Continuous Outward Spiral Pattern',
        instructionText:
          'Start from the center point, then rotate outward gradually forming an expanding spiral.',
        canvasTip:
          'Keep spacing between successive coils gradually expanding without lifting the pen.',
        tipsLabel: 'Tips:',
      },
    },
    wizard: {
      progressLabel: 'Screening Progress',
      navigationLabel: 'Step Navigation',
      inputModes: {
        canvas: 'Digital Canvas',
        upload: 'Upload Paper Photo',
      },
      backButton: 'Back',
      nextPatternButton: 'Next Pattern',
      submitButton: 'Submit & Analyze All Drawings',
      validation: {
        drawRequired: 'Please make a drawing on the canvas before proceeding to the next step.',
        fileRequired: 'Please select a drawing image file first.',
        allStepsRequired: 'Please complete all three drawing patterns (Circle, Meander, and Spiral) first.',
        analysisFailed: 'Failed to analyze screening session. Please ensure the backend is active and try again.',
        alertTitle: 'Attention',
      },
    },
    loading: {
      title: 'Processing Stroke Pattern Analysis',
      subtitle:
        'The ResNet-18 computer vision model is evaluating micromotor kinematic regularity across all three drawings and computing Late Multi-Modal Fusion...',
      srText: 'Processing analysis... Please wait a few seconds.',
    },
    canvas: {
      canvasAriaLabel: 'Drawing canvas for pattern',
      strokeLabel: 'Stroke',
      strokeOptions: {
        thin: 'Thin',
        medium: 'Medium',
        thick: 'Thick',
      },
      showGuide: 'Show Guide',
      hideGuide: 'Hide Guide',
      undo: 'Undo',
      clear: 'Clear',
    },
    upload: {
      dropzoneTitle: 'Click to select a photo or drag a file here',
      dropzoneDesc:
        'Photo of your drawing on plain white paper. Supported formats: PNG, JPG, or WebP (max. 10 MB).',
      chooseFileButton: 'Choose Paper Photo',
      changeFileButton: 'Change File',
      fileReadyText: 'File ready to process',
      previewAlt: 'Preview of uploaded file',
      invalidType: 'Unsupported file format. Please choose a PNG, JPG, or WebP image.',
      fileTooLarge: 'File size too large (maximum 10 MB).',
    },
    report: {
      title: 'Parkinson’s Pattern Screening Report',
      subtitle: 'Kinematic Stroke Evaluation Results',
      metaLabels: {
        sessionId: 'Session ID',
        completedAt: 'Completed At',
      },
      statusLabels: {
        healthy: 'Normal Movement Pattern',
        healthyShort: 'Low Risk',
        healthyDesc:
          'Your hand stroke characteristics do not show significant micromotor anomalies compared to reference models.',
        parkinson: 'Parkinson’s Pattern Indicated',
        parkinsonShort: 'Indicated',
        parkinsonDesc:
          'Indications of curvature irregularities, micrographia, or stroke fluctuations resembling Parkinson’s neuromotor characteristics were identified.',
      },
      finalVerdictLabel: 'Final Screening Verdict',
      probabilityLabel: 'Parkinson’s Probability:',
      probabilityHeading: 'Late Multi-Modal Fusion Probability Estimate',
      thresholdLabel: 'Decision Threshold',
      breakdownHeading: 'Modality-by-Modality Analysis Breakdown',
      scoreLabel: 'Parkinson’s Probability Score',
      noImageText: 'No image available',
      disclaimerTitle: 'Medical Disclaimer',
      disclaimerBody:
        'This report is generated by computational computer vision analysis and does not constitute a definitive medical diagnosis. It is intended solely as an educational and preliminary risk-screening instrument to be discussed with a neurologist if you or a loved one experience motor difficulties.',
      followUpNotice:
        'Next Steps: Consult these results with a neurologist at your nearest healthcare facility for a comprehensive clinical assessment.',
      actions: {
        printPdf: 'Print / Save Report (PDF)',
        restart: 'Start New Screening',
      },
    },
  },
};
