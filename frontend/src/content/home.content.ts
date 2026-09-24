import type { HomeContent } from './types';

export const homeContent: HomeContent = {
  hero: {
    badge: 'AI-Assisted Neuromotor Screening System',
    title: 'ParkinDraw',
    tagline: 'Draw. Analyze. Screen.',
    lead: 'Setiap goresan pena menyimpan informasi neuromuskular yang berharga. Penyakit Parkinson sering kali diawali dengan degradasi mikromotorik halus—seperti tremor tersembunyi, fluktuasi tekanan, dan osilasi spasial yang sulit terlihat oleh mata telanjang. ParkinDraw memanfaatkan jaringan konvolusional mutakhir untuk menerjemahkan pola goresan sederhana menjadi indikator penapisan risiko yang presisi, objektif, dan dapat diakses siapa saja.',
    primaryCta: 'Mulai Skrining Sekarang',
    secondaryCta: 'Pelajari Metodologi',
  },
  workflow: {
    heading: 'Dari Menggambar Menciptakan Pola',
    subtitle: 'Proses penapisan terstandarisasi yang dirancang mudah, cepat, dan terukur.',
    steps: [
      {
        number: '01',
        title: 'Gambar',
        description:
          'Ikuti pola panduan yang ditampilkan. Anda dapat menggambar langsung menggunakan layar sentuh, stylus, atau mouse pada kanvas digital, maupun menggambar manual di atas kertas putih lalu mengunggah fotonya.',
      },
      {
        number: '02',
        title: 'Analisis',
        description:
          'Gambar diproses dan dianalisis menggunakan model computer vision ResNet-18. Jaringan saraf konvolusional mendeteksi karakteristik ketidakteraturan kelengkungan, mikrografia, getaran frekuensi halus, dan diskontinuitas garis.',
      },
      {
        number: '03',
        title: 'Hasil',
        description:
          'Lihat hasil analisis sebagai bagian dari proses skrining. Dapatkan estimasi penapisan risiko terpadu berbasis penggabungan probabilitas (late fusion) ketiga gambar, lengkap dengan rincian per pola dan rekomendasi langkah tindak lanjut medis.',
      },
    ],
  },
  biomarkers: {
    heading: 'Tiga Pola. Punya Cerita.',
    subtitle: 'Dasar fisiologis dan biomekanik di balik pemilihan tiga modalitas uji gambar.',
    items: [
      {
        id: 'circle',
        name: 'Circle (Lingkaran)',
        category: 'Pola Melingkar Tertutup',
        description:
          'Pola melingkar yang digunakan sebagai salah satu bentuk gambar dalam proses analisis. Menggambar lingkaran sempurna menuntut regulasi kecepatan sudut (angular velocity) dan tekanan pena yang konstan. Pada penderita Parkinson, defisit dopamin memicu getaran mikro (micro-tremors), keraguan goresan (hesitation), serta penutupan kontur yang tidak simetris.',
      },
      {
        id: 'meander',
        name: 'Meander (Gelombang Berkelok)',
        category: 'Pola Berulang Sinusoidal',
        description:
          'Pola berulang yang merepresentasikan rangkaian gerakan tangan secara ritmis. Pola ini peka terhadap bradikinesia (kelambanan motorik) dan kekakuan otot (rigidity). Ketidakmampuan menjaga amplitudo puncak dan lembah gelombang yang seragam menjadi indikator disfungsi motorik progresif.',
      },
      {
        id: 'spiral',
        name: 'Spiral (Pilin Archimedes)',
        category: 'Pola Melingkar Berkelanjutan',
        description:
          'Pola melingkar berkelanjutan dari titik pusat ke arah luar yang membutuhkan koordinasi gerakan tangan tingkat tinggi. Merupakan uji standar klinis neurologi untuk mendeteksi mikrografia (pengecilan ukuran tulisan secara progresif), distorsi radial, dan fluktuasi tremor aksial saat mempertahankan radius lengkungan.',
      },
    ],
  },
  faqPreview: {
    heading: 'Pertanyaan yang Sering Diajukan',
    subtitle: 'Pahami hakikat penapisan, batasan teknologi, dan keamanan data Anda.',
    seeAllCta: 'Lihat Seluruh Tanya Jawab & Privasi →',
  },
  ctaBanner: {
    heading: 'Siap Melakukan Penapisan Mandiri?',
    description:
      'Hanya memerlukan beberapa menit untuk menyelesaikan tiga pola gambar. Tanpa biaya, tanpa registrasi, dan privasi Anda sepenuhnya terlindungi secara stateless.',
    buttonText: 'Mulai Sesi Skrining Sekarang',
  },
};
