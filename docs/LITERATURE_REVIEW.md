# ParkinDraw AI --- Kajian Literatur

## 1. Tujuan

Kajian literatur dilakukan sebagai landasan teknis sebelum membangun
ParkinDraw AI. Kajian ini bersifat **singkat dan project-oriented**,
bukan Systematic Literature Review (SLR).

Fokus kajian:

1.  teknik preprocessing citra handwriting/drawing;
2.  data augmentation;
3.  algoritma dan arsitektur model;
4.  hyperparameter dan tuning;
5.  strategi splitting dan validasi;
6.  evaluation metrics.

## 2. Ruang Lingkup

-   **Dataset implementasi:** NewHandPD
-   **Modalitas:** static/offline image
-   **Drawing:** Circle, Meander, Spiral
-   **Periode publikasi utama:** 2025--2026
-   **Pendekatan:** CNN, deep learning, transfer learning
-   **Target:** Healthy vs Parkinson

Literatur foundational di luar 2025--2026 dapat digunakan untuk memahami
dataset dan metodologi dasarnya.

## 3. Boolean Query

``` text
("Parkinson's disease" OR "Parkinson disease" OR Parkinson)
AND
(NewHandPD OR "New HandPD")
AND
(image OR images OR handwriting OR drawing OR spiral OR meander OR circle)
AND
(CNN OR "convolutional neural network" OR "deep learning" OR "transfer learning" OR "image classification")
AND
(classification OR detection OR diagnosis)
```

Filter tahun 2025--2026 diterapkan melalui database/search engine
akademik.

`NOT` tidak digunakan pada query utama agar penelitian multimodal yang
tetap memiliki eksperimen image-based relevan tidak terbuang.

## 4. Artikel yang Dikaji

Sebanyak **10 artikel** dikaji. Informasi yang diekstrak meliputi:

-   dataset dan jumlah subjek;
-   jenis input dan drawing;
-   preprocessing;
-   augmentation;
-   model dan arsitektur;
-   hyperparameter;
-   hyperparameter tuning;
-   splitting;
-   validation;
-   evaluation metrics;
-   hasil terbaik;
-   kelebihan dan keterbatasan.

## 5. Temuan Preprocessing

Teknik yang ditemukan antara lain:

-   resizing;
-   normalization/min-max normalization;
-   grayscale conversion;
-   thresholding/binarization;
-   cropping;
-   median/Gaussian filtering;
-   histogram equalization;
-   edge detection;
-   ROI extraction.

Penelitian yang langsung menggunakan NewHandPD menunjukkan bahwa
preprocessing relatif sederhana seperti **resize 224×224×3 dan
normalisasi** sudah dapat digunakan bersama ResNet-18.

Penelitian lain yang mencakup NewHandPD menggunakan **thresholding**
untuk mengekstrak tinta/stroke dari template.

### Keputusan

ParkinDraw menggunakan satu preprocessing pipeline tetap:

``` text
Raw Image
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

Thresholding, binarization, edge detection, dan preprocessing alternatif
tidak digunakan sebagai skenario model. Keputusan ini membatasi kebutuhan
komputasi dan menjaga pipeline training serta inference tetap sederhana.

## 6. Temuan Augmentation

Literatur menggunakan rotation, scaling, translation, zoom, flip, shear,
brightness adjustment, noise, AugMix, dan PixMix.

ParkinDraw AI memulai dengan **conservative augmentation**:

-   small rotation, dikunci sekitar ±7°;
-   small translation, dikunci sekitar ±5%;
-   small scaling, dikunci pada 0.95--1.05;
-   tanpa horizontal atau vertical flip;
-   tanpa augmentation agresif.

Augmentation hanya diterapkan pada **training data**. Transformasi
agresif tidak digunakan karena dapat mengubah karakteristik geometris
drawing. Parameter augmentation tidak menjadi Optuna search space.

## 7. Temuan Model

Model dalam literatur meliputi:

-   Custom CNN;
-   ResNet;
-   VGG;
-   EfficientNet;
-   DenseNet;
-   Inception;
-   ConvNeXt;
-   hybrid/multi-CNN;
-   kombinasi CNN dengan traditional ML.

Untuk proyek ini dipilih satu model:

-   **ImageNet-pretrained ResNet-18**;
-   seluruh backbone dibekukan;
-   hanya classification head yang dilatih.

ResNet-18 dipilih karena sudah digunakan pada penelitian NewHandPD,
kompatibel dengan input 224×224×3, relatif ringan, dan lebih
proporsional terhadap ukuran NewHandPD dibanding backbone yang jauh
lebih besar.

Custom CNN dan backbone lain tetap merupakan temuan literatur, tetapi
tidak diimplementasikan sebagai pembanding. Training from scratch,
partial-backbone fine-tuning, dan full-backbone fine-tuning juga berada
di luar scope. Pembatasan ini mengurangi jumlah skenario dan kebutuhan
komputasi.

## 8. Temuan Hyperparameter

Literatur menunjukkan bahwa learning rate, batch size, optimizer,
regularization, scheduler, dan epoch memengaruhi performa. Untuk
ParkinDraw, arsitektur dan strategi training dikunci, sedangkan pencarian
performa dibatasi pada hyperparameter optimization dengan **Optuna**.

Fixed configuration:

| Parameter | Nilai |
|---|---|
| Architecture | ResNet-18 |
| Weights | ImageNet pretrained |
| Backbone | Frozen |
| Optimizer | AdamW |
| Loss | Cross-Entropy |
| Maximum epoch | 30 |
| Early stopping | Ya |

Optuna hanya mencari learning rate, weight decay, dropout, dan batch
size. Pruning dan batas trial digunakan untuk mengendalikan komputasi.

## 9. Temuan Validasi

NewHandPD memiliki beberapa gambar dari subjek yang sama. Oleh karena
itu random image-level split berisiko menyebabkan **subject leakage**.

Strategi utama menggunakan grouped holdout test dan **Stratified Group
K-Fold** pada development set untuk Optuna.

dengan:

``` text
Target = Healthy / Parkinson
Group  = subject_id + duplicate_group
```

Semua gambar milik satu subjek dan semua exact duplicate yang saling
terkait harus berada pada fold/split yang sama.

## 10. Evaluation Metrics

Model dievaluasi menggunakan:

-   Accuracy
-   Precision
-   Recall/Sensitivity
-   Specificity
-   F1-Score
-   ROC-AUC
-   Confusion Matrix
-   Calibration curve
-   Brier score

Subject-level ROC-AUC menjadi objective utama Optuna. Accuracy tidak
digunakan sebagai satu-satunya dasar pemilihan model.

## 11. Kesimpulan Kajian

Kajian mendukung transfer learning untuk klasifikasi Parkinson berbasis
drawing. Untuk NewHandPD, ImageNet-pretrained ResNet-18 dengan input
224×224 merupakan pilihan yang relevan dan proporsional.

Implementasi dikunci pada frozen-backbone ResNet-18 dengan
classification-head-only training. Preprocessing dan augmentation
menggunakan masing-masing satu konfigurasi tetap. Optuna menjadi
satu-satunya mekanisme pencarian hyperparameter model.

Evidence eksperimen digunakan untuk menentukan hyperparameter terbaik
setiap drawing dan mengukur simple average fusion terhadap single-drawing
ablation. Evaluasi utama meniru aplikasi dengan satu Circle, satu
Meander, dan satu Spiral per screening session.

Prinsip proyek:

> Literatur digunakan untuk mengunci pipeline yang hemat komputasi,
> sedangkan Optuna dan evaluasi subject-level menentukan konfigurasi
> terbaik dalam ruang eksperimen tersebut.
