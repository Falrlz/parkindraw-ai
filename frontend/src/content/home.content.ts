import type { HomeContent } from './types';

export const homeContent: HomeContent = {
  hero: {
    title: 'PARKINDRAW',
    tagline: 'Draw. Analyze. Screen.',
  },
  explanation: {
    text:
      'Setiap goresan pena menyimpan informasi neuromuskular yang berharga. Penyakit Parkinson sering kali diawali dengan degradasi mikromotorik halus seperti tremor tersembunyi, fluktuasi tekanan, dan osilasi spasial yang sulit terlihat oleh mata telanjang. Parkindraw menganalisis pola goresan untuk mendukung deteksi dini risiko Parkinson secara cepat, non-invansif dan objektif.',
  },
  workflow: {
    heading: 'Dari Menggambar Menciptakan Pola',
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
          'Lihat hasil analisis sebagai bagian dari proses skrining. Dapatkan estimasi penapisan risiko terpadu berbasis penggabungan probabilitas ketiga gambar, lengkap dengan rincian per pola dan rekomendasi langkah tindak lanjut medis.',
      },
    ],
  },
  biomarkers: {
    heading: 'Tiga Pola. Punya Cerita.',
    items: [
      {
        id: 'circle',
        name: 'Lingkaran',
        description:
          'Pola melingkar digunakan untuk mengamati koordinasi dan konsistensi gerakan tangan. Saat menggambar, kemampuan menjaga bentuk, kelancaran, dan kestabilan goresan dapat memberikan informasi mengenai kontrol motorik halus.',
      },
      {
        id: 'meander',
        name: 'Berkelok',
        description:
          'Pola berkelok menguji kemampuan mempertahankan gerakan tangan secara ritmis dan konsisten. Perubahan pada panjang garis, jarak, dan ketegasan sudut belokan dapat mencerminkan variasi kontrol motorik selama gerakan berulang.',
      },
      {
        id: 'spiral',
        name: 'Spiral',
        description:
          'Pola spiral dari pusat ke arah luar membutuhkan koordinasi dan kontrol motorik halus. Perubahan pada keteraturan dan kerancaran garis dapat membantu mengidentifikasi karakteristik motorik terkait tremor dan gangguan gerakan.',
      },
    ],
  },
  ctaBanner: {
    heading: 'Siap Melakukan Penapisan Mandiri?',
    description:
      'Hanya memerlukan beberapa menit untuk menyelesaikan tiga pola gambar. Tanpa biaya, tanpa registrasi, dan privasi Anda sepenuhnya terlindungi secara stateless.',
    buttonText: 'Mulai Sesi Skrining Sekarang',
  },
};
