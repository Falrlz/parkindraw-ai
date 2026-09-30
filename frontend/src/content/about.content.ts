import type { Localized } from '../app/localeContext';
import type { AboutContent } from './types';

export const aboutContent: Localized<AboutContent> = {
  id: {
    hero: {
      title: 'Kecerdasan Buatan di Balik Parkindraw',
      subtitle:
        'Membedah arsitektur deep learning, formulasi fusi probabilitas, metadata teknis, dan dataset pelatihan yang mendasari sistem Parkindraw.',
    },
    aiRationale: {
      heading: 'Kecerdasan Buatan di Balik Parkindraw',
      transferLearningSubline: 'Deep Residual Learning & Frozen Backbone',
      transferLearningText:
        'Parkindraw mengadopsi paradigma Transfer Learning menggunakan arsitektur ResNet-18 (Residual Network 18-layer). Seluruh lapisan konvolusional dasar dibekukan (frozen backbone) dengan bobot prapelatihan ImageNet untuk mengekstraksi fitur visual dasar serta mengurangi risiko overfitting pada dataset dengan jumlah sampel terbatas.',
      lateFusionHeading: 'Mekanisme Late Multi-Modal Fusion',
      lateFusionSubline: 'Penggabungan Probabilitas Independen',
      lateFusionText:
        'Keputusan penapisan tidak disandarkan pada satu jenis gambar tunggal. Parkindraw menerapkan fusi keputusan multi-modal terdistribusi rata yang menggabungkan probabilitas independen dari ketiga modalitas:',
      formulaText:
        'P_fusion(Parkinson) = [ P(Circle) + P(Meander) + P(Spiral) ] / 3',
    },
    modelMetadata: {
      heading: 'Spesifikasi Teknis Model',
      subline: 'Parameter Operasional Model Runtime',
      description:
        'Konfigurasi arsitektur dan parameter yang tertanam pada runtime backend FastAPI:',
      parameterCol: 'Parameter Arsitektur',
      valueCol: 'Nilai Spesifikasi Teknis',
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
      benchmarkHeading: 'Hasil Evaluasi pada Data Uji Holdout 20%',
      benchmarkSubline: 'Evaluasi Partisi Pasien Terisolasi (Locked Partition)',
      benchmarkDescription:
        'Performa diukur secara independen pada 20% data pasien yang dikunci sejak awal dan tidak pernah terlihat selama proses pelatihan maupun validasi silang (cross-validation):',
      tableHeaders: {
        modality: 'Modalitas Uji',
        accuracy: 'Accuracy',
        precision: 'Precision',
        recall: 'Recall',
        f1Score: 'F1-Score',
        rocAuc: 'ROC-AUC',
      },
      benchmarkMetrics: [
        {
          modality: 'Lingkaran',
          accuracy: '92.31%',
          precision: '85.71%',
          recall: '100.00%',
          f1Score: '92.31%',
          rocAuc: '97.62%',
        },
        {
          modality: 'Berkelok',
          accuracy: '88.46%',
          precision: '82.14%',
          recall: '95.83%',
          f1Score: '88.46%',
          rocAuc: '93.60%',
        },
        {
          modality: 'Spiral',
          accuracy: '88.46%',
          precision: '80.00%',
          recall: '100.00%',
          f1Score: '88.89%',
          rocAuc: '99.11%',
        },
        {
          modality: 'Macro Average (Rerata)',
          accuracy: '89.74%',
          precision: '82.62%',
          recall: '98.61%',
          f1Score: '89.89%',
          rocAuc: '96.78%',
        },
      ],
      recallNote:
        'Nilai Sensitivitas/Recall rata-rata sebesar 98.61% pada data uji holdout (13 subjek) menunjukkan bahwa model sangat peka dalam menjaring potensi kasus positif Parkinson, sehingga peluang lolosnya pasien berisiko (false negative) rendah pada data uji ini.',
    },
    datasetProvenance: {
      heading: 'Dataset Pelatihan & Protokol Integritas',
      datasetName: 'NewHandPD (New Handwriting Parkinson\'s Disease Dataset)',
      sourcesHeading: 'Sumber Data & Rujukan',
      sources: [
        {
          kind: 'Dataset',
          title: 'NewHandPD',
          detail:
            'Dikumpulkan di Botucatu Medical School, São Paulo State University (UNESP), Brasil. Setiap subjek menggambar pola spiral, berkelok, dan lingkaran menggunakan pena pintar BiSP.',
          href: 'https://wwwp.fc.unesp.br/~papa/pub/datasets/Handpd/',
          hrefLabel: 'wwwp.fc.unesp.br/~papa/pub/datasets/Handpd',
        },
        {
          kind: 'Publikasi',
          title: 'Deep Learning-Aided Parkinson\'s Disease Diagnosis from Handwritten Dynamics',
          detail: 'Pereira, C. R., Weber, S. A. T., Hook, C., Rosa, G. H., & Papa, J. P.',
          meta: '29th SIBGRAPI Conference on Graphics, Patterns and Images, 2016, hlm. 340–346',
          href: 'https://doi.org/10.1109/SIBGRAPI.2016.054',
          hrefLabel: 'doi.org/10.1109/SIBGRAPI.2016.054',
        },
      ],
      subjectStats:
        'Dataset NewHandPD terdiri dari 66 subjek (31 Parkinson, 35 kontrol sehat) dengan 594 citra goresan tangan.',
      zeroLeakageProtocol:
        'Protokol Patient-Level Group Split digunakan untuk mengunci data tiap individu pada satu partisi demi mencegah bias data leakage.',
    },
  },
  en: {
    hero: {
      title: 'Artificial Intelligence Behind Parkindraw',
      subtitle:
        'An in-depth look at the deep learning architecture, probability fusion formulation, technical specifications, and training dataset powering Parkindraw.',
    },
    aiRationale: {
      heading: 'Artificial Intelligence Behind Parkindraw',
      transferLearningSubline: 'Deep Residual Learning & Frozen Backbone',
      transferLearningText:
        'Parkindraw adopts a Transfer Learning paradigm using a ResNet-18 (18-layer Residual Network) architecture. All base convolutional layers are frozen with ImageNet pre-trained weights to serve as a deterministic visual feature extractor and reduce the risk of overfitting on modest clinical datasets.',
      lateFusionHeading: 'Late Multi-Modal Fusion Mechanism',
      lateFusionSubline: 'Independent Probability Integration',
      lateFusionText:
        'Screening decisions do not rely on a single drawing type. Parkindraw applies an equally distributed multi-modal decision fusion combining independent probabilities from all three modalities:',
      formulaText:
        'P_fusion(Parkinson) = [ P(Circle) + P(Meander) + P(Spiral) ] / 3',
    },
    modelMetadata: {
      heading: 'Technical Model Specifications',
      subline: 'Runtime Model Operational Parameters',
      description:
        'Architecture configuration and operational parameters deployed on the FastAPI backend runtime:',
      parameterCol: 'Architecture Parameter',
      valueCol: 'Specification Value',
      parameters: [
        { parameter: 'Backbone Architecture', value: 'Deep Residual Network (ResNet-18)' },
        { parameter: 'Backbone Status', value: 'Frozen Convolutional Layers (Feature Extractor)' },
        {
          parameter: 'Classifier Head',
          value: 'Sequential(Dropout(p=0.0), Linear(in_features=512, out_features=2))',
        },
        { parameter: 'Input Tensor Dimensions', value: '3 × 224 × 224 (RGB, Bilinear Interpolation)' },
        {
          parameter: 'Image Normalization',
          value: 'ImageNet (μ=[0.485, 0.456, 0.406], σ=[0.229, 0.224, 0.225])',
        },
        { parameter: 'Trainable Parameters', value: '1,026 parameters (Linear Output Head)' },
        { parameter: 'Total Model Parameters', value: '11,177,538 parameters' },
        { parameter: 'Decision Threshold', value: '0.50 (Default)' },
      ],
      benchmarkHeading: 'Evaluation Results on 20% Holdout Test Set',
      benchmarkSubline: 'Isolated Patient-Level Partition Evaluation',
      benchmarkDescription:
        'Performance measured independently on 20% holdout patient data, locked from the beginning and never seen during training or cross-validation:',
      tableHeaders: {
        modality: 'Modality',
        accuracy: 'Accuracy',
        precision: 'Precision',
        recall: 'Recall',
        f1Score: 'F1-Score',
        rocAuc: 'ROC-AUC',
      },
      benchmarkMetrics: [
        {
          modality: 'Circle',
          accuracy: '92.31%',
          precision: '85.71%',
          recall: '100.00%',
          f1Score: '92.31%',
          rocAuc: '97.62%',
        },
        {
          modality: 'Meander',
          accuracy: '88.46%',
          precision: '82.14%',
          recall: '95.83%',
          f1Score: '88.46%',
          rocAuc: '93.60%',
        },
        {
          modality: 'Spiral',
          accuracy: '88.46%',
          precision: '80.00%',
          recall: '100.00%',
          f1Score: '88.89%',
          rocAuc: '99.11%',
        },
        {
          modality: 'Macro Average',
          accuracy: '89.74%',
          precision: '82.62%',
          recall: '98.61%',
          f1Score: '89.89%',
          rocAuc: '96.78%',
        },
      ],
      recallNote:
        'The average Sensitivity/Recall score of 98.61% on the holdout test set (13 subjects) indicates that the model is highly sensitive to potential positive Parkinson\'s patterns, minimizing the risk of false negatives on this test benchmark.',
    },
    datasetProvenance: {
      heading: 'Training Dataset & Integrity Protocol',
      datasetName: 'NewHandPD (New Handwriting Parkinson\'s Disease Dataset)',
      sourcesHeading: 'Data Sources & References',
      sources: [
        {
          kind: 'Dataset',
          title: 'NewHandPD',
          detail:
            'Collected at Botucatu Medical School, São Paulo State University (UNESP), Brazil. Each subject drew spiral, meander, and circle patterns using a BiSP smart pen.',
          href: 'https://wwwp.fc.unesp.br/~papa/pub/datasets/Handpd/',
          hrefLabel: 'wwwp.fc.unesp.br/~papa/pub/datasets/Handpd',
        },
        {
          kind: 'Publication',
          title: 'Deep Learning-Aided Parkinson\'s Disease Diagnosis from Handwritten Dynamics',
          detail: 'Pereira, C. R., Weber, S. A. T., Hook, C., Rosa, G. H., & Papa, J. P.',
          meta: '29th SIBGRAPI Conference on Graphics, Patterns and Images, 2016, pp. 340–346',
          href: 'https://doi.org/10.1109/SIBGRAPI.2016.054',
          hrefLabel: 'doi.org/10.1109/SIBGRAPI.2016.054',
        },
      ],
      subjectStats:
        'The NewHandPD dataset comprises 66 subjects (31 Parkinson\'s patients, 35 healthy controls) with 594 original handwriting images.',
      zeroLeakageProtocol:
        'A Patient-Level Group Split protocol was enforced to lock each individual\'s samples to a single partition, strictly preventing patient-level data leakage.',
    },
  },
};
