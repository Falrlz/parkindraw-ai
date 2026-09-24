import type { FaqContent } from './types';

export const faqContent: FaqContent = {
  title: 'Pusat Edukasi, Etika & Privasi',
  lead:
    'Temukan jawaban atas pertanyaan umum mengenai Penyakit Parkinson, dasar ilmiah analisis goresan, batasan etika klinis, serta perlindungan privasi data Anda.',
  categories: [
    {
      id: 'medis',
      title: 'Pemahaman Klinis Penyakit Parkinson',
      description: 'Dasar fisiologis, gejala motorik, dan pentingnya penapisan dini.',
      items: [
        {
          id: 'what-is-parkinson',
          question: 'Apa itu Penyakit Parkinson?',
          answer:
            'Penyakit Parkinson adalah gangguan neurodegeneratif kronis dan progresif yang terjadi ketika neuron penghasil dopamin di area substansia nigra otak mengalami kerusakan atau kematian sel. Dopamin berperan krusial dalam menyampaikan sinyal pengatur koordinasi gerakan tubuh. Penurunan kadar dopamin memicu gejala motorik khas seperti tremor saat istirahat (resting tremor), kekakuan otot (rigidity), perlambatan gerakan (bradykinesia), serta instabilitas postur tubuh.',
        },
        {
          id: 'why-drawing',
          question: 'Mengapa Menggunakan Uji Menggambar?',
          answer:
            'Aktivitas menulis dan menggambar menuntut koordinasi neuromuskular yang sangat kompleks dan terintegrasi antara korteks motorik, ganglia basalis, dan serebelum. Gerakan motorik halus ini merupakan salah satu fungsi biologis pertama yang memperlihatkan distorsi mikroskopis akibat kekurangan dopamin—bahkan sering kali muncul sebelum gejala tremor kasar terlihat jelas dalam aktivitas harian.',
        },
      ],
    },
    {
      id: 'teknologi',
      title: 'Cara Kerja & Keakuratan Sistem',
      description: 'Mekanisme kecerdasan buatan dalam mengevaluasi pola goresan.',
      items: [
        {
          id: 'what-is-parkindraw',
          question: 'Apa itu ParkinDraw?',
          answer:
            'ParkinDraw adalah platform penapisan mandiri (screening research tool) berbasis web yang memanfaatkan algoritma Computer Vision dan Deep Learning untuk menganalisis karakteristik biomekanik goresan tangan pada uji gambar Lingkaran, Meander, dan Spiral. Tujuannya adalah menyediakan akses penapisan awal yang praktis, objektif, dan non-invasif bagi masyarakat luas.',
        },
        {
          id: 'how-it-works',
          question: 'Bagaimana Cara Kerjanya?',
          answer:
            'Saat Anda menggambar atau mengunggah citra ke ParkinDraw, sistem melakukan standardisasi citra (resolusi 224 × 224 piksel dengan normalisasi ImageNet) dan mengalirkannya ke model ResNet-18 yang telah dilatih secara khusus. Model mengekstraksi representasi fitur visual yang mewakili ketidakteraturan goresan tangan. Probabilitas dari ketiga gambar kemudian digabungkan menggunakan algoritma Late Multi-Modal Fusion untuk menghasilkan estimasi penapisan risiko keseluruhan.',
        },
      ],
    },
    {
      id: 'etika-privasi',
      title: 'Batasan Klinis & Jaminan Privasi',
      description: 'Kepatuhan etika medis dan komitmen keamanan data tanpa penyimpanan.',
      items: [
        {
          id: 'is-this-diagnosis',
          question: 'Apakah Hasil Analisis ParkinDraw Merupakan Diagnosis Medis?',
          answer:
            'Bukan. ParkinDraw bukanlah alat diagnosis medis definitif. ParkinDraw adalah instrumen penapisan risiko (screening risk assessment). Hasil "Terindikasi Parkinson" hanya mengindikasikan bahwa pola goresan tangan Anda memiliki karakteristik visual dan statistik yang menyerupai sampel penderita Parkinson pada dataset pelatihan kami.',
        },
        {
          id: 'replace-doctor',
          question: 'Apakah Hasil Ini Dapat Menggantikan Pemeriksaan Dokter?',
          answer:
            'Sama sekali tidak. Diagnosis definitif Penyakit Parkinson hanya dapat ditegakkan secara sah oleh dokter spesialis saraf (neurolog) melalui serangkaian pemeriksaan neurologis komprehensif, evaluasi skala klinis UPDRS (Unified Parkinson\'s Disease Rating Scale), riwayat medis, respon terhadap terapi levodopa, serta pencitraan medis (seperti DaTscan atau MRI).',
        },
        {
          id: 'data-privacy',
          question: 'Bagaimana Kebijakan Privasi dan Keamanan Data Pengguna?',
          answer:
            'Privasi Anda adalah prioritas mutlak kami. Seluruh proses inferensi gambar pada ParkinDraw berlangsung secara Stateless In-Memory pada memori RAM server backend. Kami tidak pernah menyimpan berkas gambar, nama pasien, maupun rekaman goresan Anda ke dalam media penyimpanan hard disk ataupun basis data permanen. Begitu proses penapisan selesai dan hasil dikirimkan ke layar Anda, data gambar langsung dihapus permanen dari memori server.',
        },
      ],
    },
  ],
};
