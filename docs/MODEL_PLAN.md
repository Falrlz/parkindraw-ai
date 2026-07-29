# ParkinDraw AI --- Rancangan Model

## 1. Problem Definition

Target:

``` text
0 = Healthy
1 = Parkinson
```

Masalah merupakan **binary image classification** untuk AI-assisted
screening, bukan diagnosis medis.

Circle, Meander, dan Spiral adalah `drawing_type`, bukan label penyakit.

``` text
NewHandPD
├── Healthy (0)
│   ├── Circle
│   ├── Meander
│   └── Spiral
└── Parkinson (1)
    ├── Circle
    ├── Meander
    └── Spiral
```

## 2. Batas Eksperimen dan Komputasi

Untuk menjaga kebutuhan komputasi tetap proporsional terhadap ukuran
dataset, ruang eksperimen dikunci:

- satu arsitektur: **ImageNet-pretrained ResNet-18**;
- tidak membuat atau membandingkan Custom CNN;
- tidak membandingkan backbone lain;
- tidak melakukan training dari scratch;
- tidak melakukan full fine-tuning seluruh backbone;
- backbone ResNet-18 dibekukan;
- hanya classification head yang dilatih;
- pencarian performa model dilakukan melalui hyperparameter optimization
  dengan **Optuna**;
- Optuna menggunakan pruning dan batas trial;
- preprocessing dan augmentation menggunakan satu konfigurasi tetap;
- fusion dibatasi pada simple average menggunakan prediction yang sudah
  tersedia, sehingga tidak menambah training model.

Keputusan ini menukar luasnya perbandingan arsitektur dengan eksperimen
yang lebih fokus, reproducible, dan hemat komputasi.

## 3. Dataset

NewHandPD dilaporkan memiliki:

- 66 subjek;
- 35 Healthy;
- 31 Parkinson;
- 594 static images.

Dataset aktual memiliki satu Circle, empat Meander, dan empat Spiral per
subjek. Jumlah, identitas, serta integritasnya tetap harus ditetapkan oleh
dataset audit.

## 4. Dataset Audit

Audit dilakukan sebelum splitting dan training:

1. hitung seluruh file;
2. identifikasi class, subject ID, drawing type, dan drawing sequence;
3. periksa resolusi, channel, dan corrupted image;
4. hitung checksum;
5. temukan exact dan near-duplicate;
6. verifikasi pola filename;
7. buat metadata dan audit report;
8. tetapkan duplicate group.

Output:

``` text
data/metadata/
├── images.csv
├── audit_report.json
├── duplicate_groups.csv
└── splits/
```

Contoh metadata:

``` csv
filepath,subject_id,label,drawing_type,drawing_index,checksum,duplicate_group
HealthySpiral/sp1-H01.jpg,H01,0,spiral,1,<sha256>,<group-or-empty>
PatientSpiral/sp1-P01.jpg,P01,1,spiral,1,<sha256>,<group-or-empty>
```

Label tidak ditentukan hanya dari nama file karena pola nama
`HealthyCircle` pada dataset aktual tidak konsisten.

## 5. Data Splitting

Splitting dilakukan berdasarkan subjek dan duplicate group, bukan image.

Salah:

``` text
H01 Spiral  → Train
H01 Circle  → Test
```

Benar:

``` text
H01 → seluruh gambar berada pada partition yang sama
```

Jika gambar subjek berbeda berada dalam satu duplicate group, semua
subjek terkait juga ditempatkan pada partition yang sama.

Quality gate:

``` text
subject(train) ∩ subject(test) = ∅
duplicate_group(train) ∩ duplicate_group(test) = ∅
```

Strategi:

1. buat grouped holdout test yang dikunci;
2. gunakan Stratified Group K-Fold pada development set untuk Optuna;
3. gunakan split manifest yang sama untuk Circle, Meander, dan Spiral;
4. jangan gunakan test set untuk memilih hyperparameter, threshold, atau
   drawing type.

Konfigurasi awal yang hemat komputasi:

- grouped holdout test: sekitar 20%;
- Optuna validation: 3-fold Stratified Group K-Fold;
- stratifikasi target: Healthy/Parkinson;
- group: subject ID yang sudah dikonsolidasikan dengan duplicate group.

Rasio akhir dapat menyesuaikan hasil audit, tetapi aturan isolasi group
tidak boleh berubah.

## 6. Preprocessing Tetap

Tidak dilakukan pencarian beberapa skenario preprocessing. Pipeline
ditetapkan satu kali:

``` text
Raw Image
↓
Validate image
↓
Convert to RGB
↓
Preserve aspect ratio and pad to square
↓
Resize 224×224
↓
ResNet-18 pretrained-weights normalization
↓
Model
```

Keputusan:

- tidak menggunakan thresholding/binarization sebagai pipeline model;
- tidak menggunakan edge detection;
- tidak melakukan destructive preprocessing pada raw data;
- preprocessing validation, test, dan inference harus identik;
- implementasi preprocessing training dan inference berasal dari module
  yang sama.

Analisis visual tetap dilakukan untuk memastikan pipeline tidak
menghilangkan stroke, tetapi tidak dijadikan perbandingan model tambahan.

## 7. Data Augmentation Tetap

Augmentation hanya diterapkan pada training:

- rotasi kecil;
- translasi kecil;
- scaling kecil;
- tanpa horizontal atau vertical flip;
- tanpa transformasi agresif seperti AugMix atau PixMix.

Konfigurasi awal:

``` text
rotation    = ±7°
translation = ±5%
scale       = 0.95–1.05
```

Validation, test, dan inference tidak menerima augmentation stokastik.
Parameter augmentation tidak masuk Optuna search space agar jumlah
skenario dan kebutuhan komputasi tetap terbatas.

## 8. Model --- Frozen-Backbone ResNet-18

Model tunggal:

**ImageNet-pretrained ResNet-18**

``` text
Image
↓
Fixed preprocessing
↓
Frozen ResNet-18 backbone
↓
Trainable classification head
↓
Healthy / Parkinson probability
```

Strategi training:

1. muat pretrained weights;
2. bekukan seluruh parameter backbone;
3. pertahankan frozen backbone dan BatchNorm pada evaluation mode;
4. ganti final fully connected layer dengan classification head untuk dua
   class;
5. latih hanya classification head;
6. gunakan early stopping dan simpan best checkpoint.

Training dari scratch, unfreeze bertahap, partial-backbone fine-tuning,
dan full-backbone fine-tuning berada di luar scope saat ini.

## 9. Hyperparameter Optimization dengan Optuna

Optuna adalah satu-satunya mekanisme pencarian performa model. Arsitektur,
preprocessing, augmentation, optimizer, loss, dan freeze strategy tetap.

Fixed configuration:

| Parameter | Nilai |
|---|---|
| Architecture | ResNet-18 |
| Weights | ImageNet pretrained |
| Backbone | Frozen |
| Trainable parameters | Classification head only |
| Image size | 224×224 |
| Optimizer | AdamW |
| Loss | Cross-Entropy |
| Maximum epoch | 30 |
| Early stopping | Yes |
| Classification threshold | 0.5 |

Optuna search space awal:

| Hyperparameter | Search space |
|---|---|
| Learning rate | `1e-5` sampai `1e-2`, log scale |
| Weight decay | `1e-6` sampai `1e-3`, log scale |
| Dropout | `0.0` sampai `0.5` |
| Batch size | `16` atau `32` |

Budget awal:

- maksimal 15 trial per drawing type;
- 3-fold Stratified Group K-Fold per trial;
- Median Pruner atau pruner setara;
- trial dapat dihentikan lebih awal;
- timeout dapat digunakan sebagai batas tambahan.

Objective utama:

``` text
mean validation subject-level ROC-AUC
```

F1-score, sensitivity, specificity, dan loss tetap dicatat sebagai
secondary metrics. Search space dan budget hanya diperbesar jika terdapat
bukti bahwa hasil belum stabil dan sumber daya tersedia.

## 10. Studi per Drawing Type

Arsitektur dan pipeline sama; hanya subset `drawing_type` yang berubah.

| Study | Drawing | Model |
|---|---|---|
| STUDY-01 | Circle | Frozen-backbone ResNet-18 + Optuna |
| STUDY-02 | Meander | Frozen-backbone ResNet-18 + Optuna |
| STUDY-03 | Spiral | Frozen-backbone ResNet-18 + Optuna |

Tujuan:

> Menentukan drawing type yang paling informatif tanpa melakukan
> perbandingan arsitektur.

Ketiga study memakai test subjects, development folds, seed policy,
preprocessing, augmentation, dan Optuna budget yang sama.

## 11. Application-Matched Session Evaluation

Setiap subjek memiliki:

- satu Circle;
- empat Meander;
- empat Spiral.

Training dapat menggunakan seluruh gambar pada development partition.
Evaluation utama harus meniru aplikasi yang meminta satu gambar dari
setiap bentuk. Empat session disimulasikan untuk setiap test subject:

``` text
Session 1 = Circle + Meander-1 + Spiral-1
Session 2 = Circle + Meander-2 + Spiral-2
Session 3 = Circle + Meander-3 + Spiral-3
Session 4 = Circle + Meander-4 + Spiral-4
```

Circle digunakan kembali karena dataset hanya menyediakan satu Circle per
subjek. Metrics dihitung per application-matched session, kemudian
diringkas dengan mean dan variasi antar-session. Hasil yang merata-ratakan
keempat Meander atau Spiral boleh dilaporkan sebagai analisis tambahan,
tetapi bukan estimasi utama performa aplikasi.

Metrics:

- Accuracy
- Precision
- Recall/Sensitivity
- Specificity
- F1-Score
- ROC-AUC
- Confusion Matrix
- Calibration curve
- Brier score

Accuracy tidak digunakan sebagai satu-satunya dasar pemilihan.

## 12. Probability-Level Fusion

Fusion tidak melatih model tambahan. Metode dikunci ke simple average:

``` text
Pfinal_session =
(Pcircle + Pmeander_session + Pspiral_session) / 3
```

Weighted fusion, stacking, dan meta-classifier tidak digunakan pada scope
saat ini karena menambah parameter dan risiko overfitting.

Single-drawing result tetap dilaporkan sebagai ablation:

``` text
Best Single Drawing
        VS
Three-Drawing Average Fusion
```

Target produk tetap menggunakan tiga drawing:

``` text
Circle  ─┐
Meander ─┼→ ResNet-18 models → Average → Final Prediction
Spiral  ─┘
```

Jika fusion mengalami degradasi material terhadap single-drawing
baseline, penyebab dan dampaknya wajib didokumentasikan dan keputusan
produk ditinjau sebelum release.

## 13. Final Model Selection

Urutan pemilihan:

1. Optuna memilih hyperparameter per drawing berdasarkan validation
   subject-level ROC-AUC;
2. konfigurasi terbaik dilatih ulang pada seluruh development set;
3. setiap drawing model dievaluasi satu kali pada locked test set;
4. application-matched average fusion dievaluasi pada empat session;
5. best single drawing dilaporkan sebagai ablation;
6. ketiga model dan average fusion menjadi target inference
   configuration.

Test set tidak digunakan untuk:

- memilih Optuna trial;
- memperbesar search space;
- mengubah augmentation;
- mengubah classification threshold;
- memilih checkpoint.

Classification threshold dikunci pada `0.5` dalam scope awal. Analisis
threshold lain boleh dilaporkan sebagai future work, bukan digunakan
untuk menaikkan hasil test.

## 14. Experiment Tracking dan Artifact

Semua study dilacak dengan MLflow.

Setiap run minimal mencatat:

- dataset dan split version;
- drawing type;
- pretrained weights identifier;
- freeze strategy;
- Optuna study dan trial number;
- hyperparameter;
- fold metrics;
- subject-level predictions;
- training duration;
- best checkpoint;
- confusion matrix, ROC, dan calibration plot;
- code revision jika repository Git sudah aktif.

Artifact deployment minimal:

``` text
model.pt
manifest.json
preprocessing.json
class_mapping.json
threshold.json
metrics.json
```

Jika average fusion menang, manifest juga mencatat ketiga model version
dan aggregation method.

## 15. Model Workflow

``` text
Dataset Audit
↓
Metadata and Duplicate Groups
↓
Locked Grouped Test Split
↓
Fixed Preprocessing and Augmentation
↓
Frozen-Backbone ResNet-18
↓
Optuna: Circle / Meander / Spiral
↓
Refit Best Trial per Drawing
↓
Application-Matched Session Evaluation
↓
Three-Drawing Average Fusion + Single-Drawing Ablation
↓
Final Inference Artifact
```

## 16. Keputusan yang Dikunci

- satu model architecture: ResNet-18;
- ImageNet pretrained weights;
- backbone frozen;
- classification head only training;
- tidak menggunakan Custom CNN;
- tidak melakukan training from scratch;
- tidak melakukan partial atau full-backbone fine-tuning;
- satu preprocessing pipeline;
- satu conservative augmentation policy;
- Optuna sebagai satu-satunya hyperparameter search;
- AdamW dan Cross-Entropy;
- threshold awal `0.5`;
- satu Circle, satu Meander, dan satu Spiral per screening session;
- application-matched session evaluation;
- simple average untuk fusion;
- MLflow experiment tracking.

## 17. Keputusan yang Masih Bergantung pada Evidence

- Optuna hyperparameter terbaik untuk setiap drawing;
- drawing type terbaik;
- besarnya peningkatan atau degradasi fusion terhadap single-drawing
  ablation;
- final model artifact yang digunakan inference.
