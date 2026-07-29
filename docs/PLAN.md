# ParkinDraw AI --- Project Plan

## 1. Tujuan

Dokumen ini merupakan single source of truth untuk urutan pengerjaan
ParkinDraw. Detail arsitektur model berada di `MODEL_PLAN.md`, sedangkan
detail folder berada di `PROJECT_STRUCTURE.md`.

Target akhir:

> Membangun aplikasi AI-assisted Parkinson's screening yang menerima satu
> Circle, satu Meander, dan satu Spiral, lalu menggabungkan probabilitas
> ketiga model melalui simple average fusion.

Output sistem adalah prediction/screening berbasis model, bukan diagnosis
medis atau pengganti tenaga kesehatan.

## 2. Status Saat Ini

Tanggal pembaruan: **29 Juli 2026**

| Area | Status |
|---|---|
| Branding dan positioning | Selesai |
| Kajian literatur awal | Selesai |
| Rancangan model | Selesai |
| Rancangan struktur repository | Selesai |
| Dataset NewHandPD | Sudah tersedia secara lokal |
| Audit dataset pendahuluan | Selesai, belum reproducible |
| Repository Git | Belum diinisialisasi |
| Dataset pipeline | Belum dimulai |
| Training dan Optuna | Belum dimulai |
| Backend dan frontend | Belum dimulai |

Temuan audit pendahuluan yang wajib diverifikasi oleh pipeline:

- 594 gambar dari 66 subjek;
- 35 Healthy dan 31 Parkinson;
- satu Circle, empat Meander, dan empat Spiral per subjek;
- pola nama `HealthyCircle` tidak konsisten dengan class;
- terdapat exact duplicate antarsubjek pada Patient Meander dan Spiral;
- raw image memiliki resolusi yang bervariasi.

Audit pendahuluan bukan artifact final dan tidak menggantikan script,
metadata, serta test yang reproducible.

## 3. Keputusan yang Dikunci

### Produk

- user mengirim satu Circle, satu Meander, dan satu Spiral;
- ketiga input wajib tersedia untuk screening;
- prediction digabung dengan simple average fusion;
- hasil selalu disertai disclaimer non-diagnostik;
- raw user drawing tidak disimpan secara default.

### Machine Learning

- satu architecture: ImageNet-pretrained ResNet-18;
- backbone dibekukan;
- hanya classification head yang dilatih;
- tidak menggunakan Custom CNN;
- tidak melakukan training from scratch atau full fine-tuning;
- preprocessing dan augmentation menggunakan konfigurasi tetap;
- Optuna menjadi satu-satunya hyperparameter search;
- Optuna memakai pruning dan compute budget;
- split berbasis subject dan duplicate group;
- test set dikunci sebelum tuning;
- MLflow digunakan untuk experiment tracking.

### Repository

- hybrid monorepo;
- satu Python package di `src/parkindraw/`;
- backend tidak menduplikasi preprocessing atau model;
- dataset, model binary, MLflow runtime data, dan artikel PDF tidak masuk
  Git;
- folder dibuat bertahap ketika memiliki isi dan tanggung jawab nyata.

## 4. Alur dan Dependensi Fase

``` text
Phase 0  Repository Foundation
   ↓
Phase 1  Data Governance and Reproducible Audit
   ↓
Phase 2  Input Protocol, Metadata, and Leakage-Safe Splits
   ↓
Phase 3  Fixed ML Pipeline and ResNet-18 Smoke Run
   ↓
Phase 4  Optuna Studies per Drawing
   ↓
Phase 5  Application-Matched Evaluation and Fusion
   ↓
Phase 6  Inference Package and MLOps
   ↓
Phase 7  FastAPI Backend
   ↓
Phase 8  React Frontend
   ↓
Phase 9  Monitoring, Deployment, and Release
```

Suatu fase hanya dinyatakan selesai setelah exit criteria-nya terpenuhi.
Fase berikutnya boleh dipersiapkan, tetapi tidak boleh mengabaikan quality
gate fase sebelumnya.

## 5. Phase 0 --- Repository Foundation

Status: **In progress**

### Tujuan

Membentuk repository yang bersih sebelum source code dan artifact
bertambah.

### Pekerjaan

- tentukan `LICENSE`;
- buat `README.md`, `CITATION.cff`, `.gitignore`, `.gitattributes`, dan
  `.editorconfig`;
- buat `pyproject.toml` dan tetapkan versi Python;
- gunakan `uv.lock` setelah dependency awal dikunci;
- buat package minimum `src/parkindraw/__init__.py`;
- gunakan `D:\project\parkindraw-ai\parkindraw-ai` sebagai repository
  root;
- pindahkan dataset dari workspace induk sebagai satu unit ke
  `data/raw/newhandpd/`;
- pindahkan material kajian dari workspace induk ke
  `research/literature/`;
- jangan commit raw dataset dan artikel PDF;
- inisialisasi Git dengan branch `main`;
- tinjau seluruh staged file sebelum initial commit;
- buat repository GitHub dan push initial commit.

### Deliverable

- repository root sesuai `PROJECT_STRUCTURE.md`;
- initial commit tanpa data, secret, cache, PDF, atau model binary;
- dokumentasi awal dapat dibaca melalui GitHub.

### Exit Criteria

- `git status` bersih setelah commit;
- file dataset terbukti di-ignore;
- file artikel PDF terbukti di-ignore;
- tidak ada secret pada tracked files;
- package `parkindraw` dapat di-import dalam development environment.

## 6. Phase 1 --- Data Governance and Reproducible Audit

Status: **Not started**

### Tujuan

Mengubah inspeksi manual menjadi dataset audit yang dapat dijalankan ulang.

### Pekerjaan

- implementasikan image discovery;
- normalisasikan class, subject ID, drawing type, dan drawing index;
- jangan menentukan class hanya dari nama file;
- hitung SHA-256;
- validasi image readability, channel, dan resolusi;
- deteksi exact duplicate;
- siapkan hook atau laporan untuk near-duplicate analysis;
- verifikasi anomali `mea5-P8`;
- verifikasi kelompok duplicate terhadap sumber dataset;
- dokumentasikan sumber, lisensi, dan aturan penggunaan NewHandPD;
- buat automated data tests.

### Deliverable

``` text
data/metadata/
├── images.csv
├── subjects.csv
├── audit_report.json
└── duplicate_groups.csv
```

Tambahan:

- `src/parkindraw/data/audit.py`;
- `src/parkindraw/data/metadata.py`;
- `tests/data/`;
- `docs/DATA_CARD.md`.

### Exit Criteria

- seluruh 594 file memiliki record metadata;
- tidak ada image unreadable yang tidak dijelaskan;
- setiap record memiliki class, normalized subject ID, drawing type, dan
  drawing index yang valid;
- exact duplicate tercatat;
- keputusan duplicate handling terdokumentasi;
- data tests lulus.

## 7. Phase 2 --- Input Protocol, Metadata, and Leakage-Safe Splits

Status: **Not started**

### Tujuan

Mengunci protokol input aplikasi dan menghasilkan split yang aman dari
subject serta duplicate leakage.

### Pekerjaan

- tetapkan format input: upload gambar, foto template, atau canvas;
- dokumentasikan template Circle, Meander, dan Spiral;
- bandingkan secara visual domain input aplikasi dengan NewHandPD;
- jika menggunakan canvas digital, nyatakan bahwa generalisasi dari scan
  ke canvas belum tervalidasi tanpa data tambahan;
- bentuk effective group dari subject ID dan duplicate group;
- buat grouped holdout test;
- buat 3-fold Stratified Group K-Fold pada development set;
- simpan split sebagai manifest, bukan salinan folder gambar;
- buat application-matched evaluation sessions.

Dataset menyediakan empat Meander dan empat Spiral per subjek, sedangkan
aplikasi meminta satu dari setiap bentuk. Training dapat menggunakan semua
gambar, tetapi evaluation utama harus mensimulasikan:

``` text
Session 1 = Circle + Meander-1 + Spiral-1
Session 2 = Circle + Meander-2 + Spiral-2
Session 3 = Circle + Meander-3 + Spiral-3
Session 4 = Circle + Meander-4 + Spiral-4
```

### Deliverable

``` text
data/metadata/splits/
├── holdout.csv
├── optuna_fold_0.csv
├── optuna_fold_1.csv
└── optuna_fold_2.csv
```

Tambahan:

- input protocol specification;
- session manifest;
- split and leakage tests.

### Exit Criteria

``` text
subject(train) ∩ subject(test) = ∅
duplicate_group(train) ∩ duplicate_group(test) = ∅
```

Selain itu:

- class distribution setiap partition terdokumentasi;
- split reproducible dengan seed dan manifest;
- ketiga drawing type memakai assignment subject yang sama;
- protokol aplikasi dan batas domain generalization terdokumentasi.

## 8. Phase 3 --- Fixed ML Pipeline and ResNet-18 Smoke Run

Status: **Not started**

### Tujuan

Membuktikan pipeline end-to-end dapat berjalan sebelum Optuna.

### Pekerjaan

- implementasikan dataset loader berbasis metadata;
- implementasikan fixed preprocessing;
- implementasikan fixed conservative augmentation;
- muat ImageNet-pretrained ResNet-18;
- bekukan seluruh backbone dan BatchNorm;
- buat trainable two-class classification head;
- implementasikan training loop, validation, early stopping, dan
  checkpointing;
- implementasikan subject/session-level metrics;
- integrasikan local MLflow tracking;
- jalankan smoke training dengan subset kecil.

### Deliverable

- `src/parkindraw/preprocessing/`;
- `src/parkindraw/models/resnet18.py`;
- `src/parkindraw/training/`;
- `src/parkindraw/evaluation/`;
- initial experiment configuration;
- unit dan integration tests.

### Exit Criteria

- hanya classification head memiliki `requires_grad=True`;
- satu training run dapat direproduksi dari config;
- train dan validation loss tercatat;
- checkpoint dapat dimuat ulang;
- inference preprocessing sama dengan evaluation preprocessing;
- MLflow mencatat config, metrics, dan artifact.

## 9. Phase 4 --- Optuna Studies per Drawing

Status: **Not started**

### Tujuan

Menemukan hyperparameter classification head terbaik untuk setiap drawing
type dengan compute budget yang terkendali.

### Pekerjaan

- buat study terpisah untuk Circle, Meander, dan Spiral;
- gunakan fold, seed policy, preprocessing, dan augmentation yang sama;
- cari learning rate, weight decay, dropout, dan batch size;
- gunakan maximum 15 trial per drawing sebagai budget awal;
- gunakan pruner dan optional timeout;
- gunakan mean validation subject-level ROC-AUC sebagai objective;
- catat secondary metrics dan runtime;
- jangan akses locked test set.

### Deliverable

- tiga Optuna studies;
- best parameter per drawing;
- optimization history;
- fold metrics;
- MLflow run links/IDs;
- reproducible study summary.

### Exit Criteria

- seluruh study menggunakan search space dan budget yang tercatat;
- pruned dan completed trials dapat ditelusuri;
- best trial tidak dipilih menggunakan test set;
- best configuration setiap drawing dapat dijalankan ulang.

## 10. Phase 5 --- Application-Matched Evaluation and Fusion

Status: **Not started**

### Tujuan

Mengukur performa pada kondisi yang menyerupai satu screening session di
aplikasi.

### Pekerjaan

- refit best configuration setiap drawing pada seluruh development set;
- evaluasi satu kali pada locked test set;
- jalankan empat application-matched session simulations;
- hitung metrics per drawing;
- hitung simple average fusion:

``` text
Pfinal = (Pcircle + Pmeander + Pspiral) / 3
```

- laporkan mean dan variasi performa antar-session;
- bandingkan fusion dengan single-drawing result sebagai ablation;
- dokumentasikan limitation akibat ukuran dataset dan domain input.

### Deliverable

- final test predictions;
- confusion matrix, ROC, calibration, dan Brier score;
- session-level evaluation report;
- three-model fusion manifest;
- model card draft.

### Exit Criteria

- test set hanya digunakan setelah keputusan training dikunci;
- setiap fused prediction memakai satu Circle, satu Meander, dan satu
  Spiral dari subjek yang sama;
- hasil fusion, ablation, dan limitation dilaporkan tanpa cherry-picking;
- ketiga model artifact dan fusion rule teridentifikasi secara unik.

Jika fusion menunjukkan degradasi material, penyebabnya harus
didokumentasikan dan keputusan produk ditinjau sebelum release. Hasil
tidak boleh disembunyikan hanya untuk mempertahankan desain UI.

## 11. Phase 6 --- Inference Package and MLOps

Status: **Not started**

### Tujuan

Mengubah hasil eksperimen menjadi artifact inference yang reproducible.

### Pekerjaan

- buat loader untuk model artifact dan manifest;
- buat typed prediction result;
- implementasikan triplet inference;
- validasi urutan dan drawing type;
- implementasikan average fusion;
- tetapkan threshold `0.5`;
- simpan class mapping dan preprocessing identifier;
- siapkan MLflow tracking server configuration;
- dokumentasikan model promotion dan rollback.

### Deliverable

``` text
model-circle.pt
model-meander.pt
model-spiral.pt
manifest.json
preprocessing.json
class_mapping.json
threshold.json
metrics.json
```

### Exit Criteria

- artifact checksum tervalidasi;
- prediction yang sama menghasilkan output deterministik;
- ketiga model dan fusion config dapat dimuat dari manifest;
- inference package tidak mengimpor backend;
- smoke test inference lulus.

## 12. Phase 7 --- FastAPI Backend

Status: **Not started**

### Tujuan

Menyediakan inference melalui API yang tervalidasi dan observable.

### Pekerjaan

- implementasikan application lifespan dan model loading;
- buat `/api/v1/health`;
- buat `/api/v1/model-info`;
- buat `/api/v1/screening`;
- validasi tiga input wajib;
- validasi MIME type, ukuran, dan image readability;
- map error ke response yang aman;
- tambahkan request ID, structured logging, latency, dan error metrics;
- batasi CORS melalui configuration;
- jangan menyimpan user drawing secara default;
- buat unit, integration, dan API contract tests.

### Exit Criteria

- API menolak input yang hilang atau tidak valid;
- health endpoint membedakan liveness dan model readiness;
- screening response sesuai schema;
- model hanya dimuat sekali per worker lifecycle;
- API test suite lulus;
- disclaimer tersedia pada response atau product contract.

## 13. Phase 8 --- React Frontend

Status: **Not started**

### Tujuan

Menyediakan alur screening tiga drawing yang jelas dan konsisten dengan
protokol model.

### Pekerjaan

- implementasikan landing dan disclaimer;
- implementasikan instruksi drawing;
- implementasikan input Circle, Meander, dan Spiral;
- tampilkan preview dan status validasi;
- cegah submission sebelum ketiga input lengkap;
- integrasikan API client;
- tampilkan probability dan screening result secara non-diagnostik;
- sediakan error, retry, loading, dan accessibility states;
- dukung Indonesian dan English jika tetap menjadi product requirement;
- buat component dan end-to-end tests.

### Exit Criteria

- user tidak dapat menukar drawing type tanpa peringatan;
- request selalu memiliki tiga field yang tepat;
- UI tidak mengklaim diagnosis;
- error API dapat dipahami user;
- mobile dan desktop flow dapat digunakan;
- frontend tests lulus.

## 14. Phase 9 --- Monitoring, Deployment, and Release

Status: **Not started**

### Tujuan

Menyediakan deployment yang dapat direproduksi dan dipantau.

### Pekerjaan

- buat production Dockerfile untuk backend dan frontend;
- buat local `docker-compose.yml`;
- tambahkan Prometheus metrics;
- buat Grafana dashboard;
- buat CI untuk Python quality, backend tests, dan frontend tests;
- konfigurasi environment dan secret injection;
- buat deployment smoke test;
- finalisasi README, architecture document, data card, dan model card;
- dokumentasikan backup, rollback, dan incident procedure;
- buat release tag.

### Exit Criteria

- clean environment dapat menjalankan build;
- CI wajib lulus sebelum merge;
- health, latency, error rate, dan inference count terlihat;
- tidak ada dataset, user drawing, secret, atau model internal yang
  terekspos tanpa keputusan eksplisit;
- release documentation lengkap;
- production disclaimer terlihat.

## 15. Risiko Utama

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Subject leakage | Metrics terlalu optimistis | Grouped split dan automated leakage test |
| Duplicate antarsubjek | Leakage lintas group | Duplicate manifest dan effective group |
| Dataset kecil | Variansi dan overfitting | Frozen backbone, pruning, grouped validation |
| Scan-to-canvas domain shift | Model gagal pada input aplikasi | Kunci input protocol dan validasi domain |
| Hanya satu dataset | Generalisasi tidak diketahui | Model card dan external validation future work |
| Medical overclaim | Risiko etik dan komunikasi | Screening terminology dan disclaimer |
| Dataset/PDF masuk Git | Lisensi dan repository bloat | `.gitignore` dan staged-file review |
| Training-serving skew | API berbeda dari evaluation | Shared `parkindraw.inference` package |

## 16. Quality Gates Global

Setiap perubahan harus menjaga:

- raw dataset immutable;
- tidak ada subject atau duplicate leakage;
- konfigurasi dan seed tercatat;
- training, evaluation, dan inference memakai preprocessing yang sama;
- test set tidak digunakan untuk tuning;
- artifact memiliki manifest dan checksum;
- secret, dataset, PDF, dan runtime artifact tidak masuk Git;
- hasil negatif atau limitation tidak disembunyikan;
- komunikasi produk tidak menggunakan klaim diagnosis.

## 17. Strategi Commit

Commit dibuat kecil dan mengikuti deliverable:

``` text
chore: initialize ParkinDraw project foundation
feat(data): add reproducible NewHandPD audit
feat(data): add leakage-safe split manifests
feat(ml): add frozen ResNet-18 training pipeline
feat(ml): add Optuna optimization workflow
feat(eval): add application-matched fusion evaluation
feat(inference): add versioned triplet predictor
feat(api): add screening endpoints
feat(web): add three-drawing screening flow
chore(ops): add monitoring and deployment configuration
```

Generated data, metrics, dan model binary tidak dicampur dengan source
code commit kecuali merupakan selected report atau manifest yang memang
ditetapkan untuk version control.

## 18. Definition of Done

ParkinDraw dinyatakan mencapai versi awal ketika:

1. dataset audit dan split dapat direproduksi;
2. leakage tests lulus;
3. tiga frozen-backbone ResNet-18 selesai dioptimasi dengan Optuna;
4. locked-test evaluation selesai tanpa test-driven tuning;
5. one-Circle, one-Meander, one-Spiral fusion tersedia;
6. artifact inference memiliki manifest dan checksum;
7. FastAPI serta React terintegrasi;
8. automated tests dan CI lulus;
9. monitoring dasar aktif;
10. data card, model card, limitation, dan disclaimer dipublikasikan.
