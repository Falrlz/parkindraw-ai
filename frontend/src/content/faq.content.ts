import type { Localized } from '../app/localeContext';
import type { FaqContent } from './types';

export const faqContent: Localized<FaqContent> = {
  id: {
    heading: 'Pertanyaan yang Sering Diajukan',
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
          'Aktivitas menulis dan menggambar menuntut koordinasi neuromuskular yang sangat kompleks dan terintegrasi antara korteks motorik, ganglia basalis, dan serebelum. Gerakan motorik halus ini merupakan salah satu fungsi biologis pertama yang memperlihatkan distorsi mikroskopis akibat kekurangan dopamin, bahkan sering kali muncul sebelum gejala tremor kasar terlihat jelas dalam aktivitas harian.',
      },
      {
        id: 'what-is-parkindraw',
        question: 'Apa itu Parkindraw?',
        answer:
          'Parkindraw adalah platform skrining berbasis kecerdasan buatan (AI) yang menganalisis perubahan mikromotorik halus pada goresan tangan melalui uji pola gambar Lingkaran, Berkelok (Meander), dan Spiral. Dengan memanfaatkan teknologi computer vision dan deep learning, Parkindraw dirancang untuk mendukung deteksi dini risiko Parkinson secara cepat, objektif, dan non-invasif.',
      },
      {
        id: 'how-it-works',
        question: 'Bagaimana Cara Kerjanya?',
        answer:
          'Saat Anda menggambar atau mengunggah citra ke Parkindraw, sistem melakukan standardisasi citra (resolusi 224 × 224 piksel dengan normalisasi ImageNet) dan mengalirkannya ke model ResNet-18 yang telah dilatih secara khusus. Model mengekstraksi representasi fitur visual yang mewakili ketidakteraturan goresan tangan. Probabilitas dari ketiga gambar kemudian digabungkan menggunakan algoritma Late Multi-Modal Fusion untuk menghasilkan estimasi penapisan risiko keseluruhan.',
      },
      {
        id: 'is-this-diagnosis',
        question: 'Apakah Hasil Analisis Parkindraw Merupakan Diagnosis Medis?',
        answer:
          'Bukan. Parkindraw bukanlah alat diagnosis medis definitif. Parkindraw adalah instrumen penapisan risiko (screening risk assessment). Hasil "Terindikasi Parkinson" hanya mengindikasikan bahwa pola goresan tangan Anda memiliki karakteristik visual dan statistik yang menyerupai sampel penderita Parkinson pada dataset pelatihan kami.',
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
          'Privasi Anda adalah prioritas mutlak kami. Seluruh proses inferensi gambar pada Parkindraw berlangsung secara Stateless In-Memory pada memori RAM server backend. Kami tidak pernah menyimpan berkas gambar, nama pasien, maupun rekaman goresan Anda ke dalam media penyimpanan hard disk ataupun basis data permanen. Begitu proses penapisan selesai dan hasil dikirimkan ke layar Anda, data gambar langsung dihapus permanen dari memori server.',
      },
    ],
  },
  en: {
    heading: 'Frequently Asked Questions',
    items: [
      {
        id: 'what-is-parkinson',
        question: 'What is Parkinson’s Disease?',
        answer:
          'Parkinson’s disease is a chronic and progressive neurodegenerative disorder caused by the loss or degeneration of dopamine-producing neurons in the substantia nigra region of the brain. Dopamine plays a vital role in transmitting signals that control bodily movement coordination. The reduction of dopamine levels leads to characteristic motor symptoms such as resting tremors, muscle rigidity, slowness of movement (bradykinesia), and postural instability.',
      },
      {
        id: 'why-drawing',
        question: 'Why Use Drawing Tests?',
        answer:
          'Writing and drawing activities demand highly integrated and complex neuromuscular coordination between the motor cortex, basal ganglia, and cerebellum. Fine micromotor control is often among the earliest biological functions to exhibit subtle distortions resulting from dopamine deficiency, frequently manifesting well before gross resting tremors become visible during daily activities.',
      },
      {
        id: 'what-is-parkindraw',
        question: 'What is Parkindraw?',
        answer:
          'Parkindraw is an artificial intelligence (AI) screening platform that analyzes fine micromotor changes in hand drawings through Circle, Meander, and Spiral pattern tests. By leveraging computer vision and deep learning technologies, Parkindraw is designed to support rapid, objective, and non-invasive early detection of Parkinson’s risk.',
      },
      {
        id: 'how-it-works',
        question: 'How Does It Work?',
        answer:
          'When you draw or upload images to Parkindraw, the system standardizes each drawing (224 × 224 pixel resolution with ImageNet normalization) and passes it through a specialized ResNet-18 model. The model extracts visual feature representations of kinematic irregularities. Probabilities from all three drawings are then combined using a Late Multi-Modal Fusion algorithm to produce an integrated overall risk assessment.',
      },
      {
        id: 'is-this-diagnosis',
        question: 'Is Parkindraw Analysis a Definitive Medical Diagnosis?',
        answer:
          'No. Parkindraw is not a definitive medical diagnostic tool. It is a risk screening instrument (screening risk assessment). An "Indicated" result merely suggests that your drawing patterns share visual and statistical characteristics with Parkinson’s patient samples in our training dataset.',
      },
      {
        id: 'replace-doctor',
        question: 'Can This Result Replace a Clinical Doctor\'s Examination?',
        answer:
          'Not at all. A definitive diagnosis of Parkinson’s disease can only be established by a qualified neurologist through comprehensive neurological evaluations, clinical UPDRS (Unified Parkinson’s Disease Rating Scale) scoring, medical history, response to levodopa therapy, and neuroimaging (such as DaTscan or MRI).',
      },
      {
        id: 'data-privacy',
        question: 'What is the Data Privacy and Security Policy?',
        answer:
          'Your privacy is our utmost priority. All image inference processes on Parkindraw execute Stateless In-Memory on the backend server’s RAM. We never store image files, personal identifiers, or drawing strokes on disk or permanent databases. Once the screening process completes and results are delivered to your device, the image data is immediately purged from memory.',
      },
    ],
  },
};
