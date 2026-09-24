import type { AboutContent } from './types';

export const aboutContent: AboutContent = {
  hero: {
    title: 'Kecerdasan Buatan & Transparansi Sains',
    subtitle:
      'Membedah arsitektur deep learning, formulasi fusi probabilitas, metadata teknis, dan dataset pelatihan yang mendasari sistem ParkinDraw AI.',
  },
  aiRationale: {
    heading: 'Kecerdasan Buatan di Balik ParkinDraw',
    transferLearningText:
      'ParkinDraw mengadopsi paradigma Transfer Learning menggunakan arsitektur ResNet-18 (Residual Network 18-layer). Seluruh lapisan konvolusional dasar dibekukan (frozen backbone) dengan bobot prapelatihan ImageNet. Pendekatan ini memungkinkan model bertindak sebagai ekstraktor fitur visual deterministik yang sangat andal tanpa risiko overfitting (penghafalan data berlebih) pada dataset citra medis berukuran terukur.',
    lateFusionHeading: 'Mekanisme Late Multi-Modal Fusion',
    lateFusionText:
      'Keputusan penapisan tidak disandarkan pada satu jenis gambar tunggal. ParkinDraw menerapkan fusi keputusan multi-modal terdistribusi rata yang menggabungkan probabilitas independen dari ketiga modalitas:',
    formulaText:
      'P_fusion(Parkinson) = [ P(Circle) + P(Meander) + P(Spiral) ] / 3',
  },
  modelMetadata: {
    heading: 'Spesifikasi Teknis Model',
    description:
      'Konfigurasi arsitektur dan parameter yang tertanam pada runtime backend FastAPI:',
    parameters: [
      { parameter: 'Arsitektur Backbone', value: 'Deep Residual Network (ResNet-18)' },
      { parameter: 'Kondisi Backbone', value: 'Frozen Convolutional Layers (Feature Extractor)' },
      {
        parameter: 'Classifier Head',
        value: 'Sequential(Dropout(p=0.0), Linear(in_features=512, out_features=2))',
      },
      { parameter: 'Dimensi Masukan Tensor', value: '3 × 224 × 224 (RGB, Interpolasi Bilinear)' },
      {
        parameter: 'Normalisasi Citra',
        value: 'ImageNet (μ=[0.485, 0.456, 0.406], σ=[0.229, 0.224, 0.225])',
      },
      { parameter: 'Parameter Aktif Dilatih', value: '1.026 parameter (Linear Output Head)' },
      { parameter: 'Parameter Total Model', value: '11.177.538 parameter' },
      { parameter: 'Ambang Batas Keputusan (Threshold)', value: '0.50 (Default)' },
    ],
    benchmarkHeading: 'Hasil Evaluasi pada Data Uji Terkunci (Holdout 20%)',
    benchmarkDescription:
      'Performa diukur secara independen pada 20% data pasien yang dikunci sejak awal dan tidak pernah terlihat selama proses pelatihan maupun validasi silang (cross-validation):',
    benchmarkMetrics: [
      {
        modality: 'Circle (Lingkaran)',
        accuracy: '92.31%',
        precision: '85.71%',
        recall: '100.00%',
        f1Score: '0.9231',
        rocAuc: '0.9904',
      },
      {
        modality: 'Meander (Gelombang)',
        accuracy: '88.46%',
        precision: '82.14%',
        recall: '95.83%',
        f1Score: '0.8846',
        rocAuc: '0.9519',
      },
      {
        modality: 'Spiral (Pilin)',
        accuracy: '88.46%',
        precision: '80.00%',
        recall: '100.00%',
        f1Score: '0.8889',
        rocAuc: '0.9610',
      },
      {
        modality: 'Macro Average (Rerata)',
        accuracy: '89.74%',
        precision: '82.62%',
        recall: '98.61%',
        f1Score: '0.8989',
        rocAuc: '0.9678',
      },
    ],
    recallNote:
      'Nilai Sensitivitas/Recall rata-rata sebesar 98.61% membuktikan bahwa model sangat peka dalam menjaring potensi kasus positif Parkinson sehingga meminimalkan peluang lolosnya pasien berisiko (false negative sangat rendah).',
  },
  datasetProvenance: {
    heading: 'Dataset Pelatihan & Protokol Integritas',
    datasetName: 'NewHandPD (New Handwriting Parkinson\'s Disease Dataset)',
    institutions: [
      'Laboratorium Komputasi Terapan & Pembelajaran Mesin, Federal University of São Carlos (UFSCar), Brasil',
      'São Paulo State University (UNESP), Bauru, Brasil',
    ],
    citations: [
      {
        authors: 'Pereira, C. R., et al.',
        title:
          'A new computer vision-based approach to aid the diagnosis of Parkinson\'s disease using offline handwriting images',
        journal: 'Information Sciences / Elsevier',
      },
      {
        authors: 'Kansizoglou, I., et al. (2025)',
        title:
          'Drawing-Aware Parkinson\'s Disease Detection Through Hierarchical Deep Learning Models',
        journal: 'IEEE Transactions / Springer',
      },
    ],
    subjectStats:
      'Total 66 subjek (31 pasien terdiagnosis klinis Parkinson dan 35 subjek kontrol sehat yang sebanding secara demografis), menghasilkan 594 citra goresan tangan asli.',
    zeroLeakageProtocol:
      'Pembagian partisi data menerapkan protokol ketat Patient-Level Group Split. Seluruh sampel dari satu individu yang sama dikunci dalam fold yang sama dan tidak pernah terbagi antara data latih dan data uji holdout. Protokol ini menjamin evaluasi performa model bebas sepenuhnya dari bias kebocoran data klinis (zero clinical data leakage).',
  },
};
