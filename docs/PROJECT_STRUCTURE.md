# ParkinDraw AI --- Struktur Proyek

## 1. Keputusan Arsitektur

ParkinDraw menggunakan **hybrid monorepo** dengan pendekatan:

- **Python `src` layout** untuk seluruh core machine learning;
- **ML lifecycle structure** untuk data, eksperimen, model, dan laporan;
- **layer-based structure** yang sederhana untuk backend FastAPI;
- **feature-based structure** untuk frontend React;
- **modular monolith** sebagai arsitektur aplikasi;
- konfigurasi MLOps dan monitoring dikelompokkan sebagai infrastruktur.

Struktur ini dipilih karena ParkinDraw merupakan satu produk yang terdiri
dari penelitian data, training model, inference API, dan web application.
Semua komponen perlu berkembang bersama tanpa kompleksitas microservices
atau polyrepo.

## 2. Prinsip

### 2.1 Satu Repository Root

`parkindraw-ai/` adalah satu-satunya repository root. Folder induk boleh
berfungsi sebagai workspace yang menyimpan bahan awal di luar repository,
tetapi jangan membuat folder `parkindraw-ai/` lagi di dalam repository
root.

### 2.2 Raw Data Bersifat Immutable

Dataset asli:

- tidak di-resize;
- tidak di-rename massal;
- tidak di-augment;
- tidak di-overwrite;
- tidak disimpan langsung di Git.

Semua koreksi nama, label, subject ID, dan duplicate group dicatat dalam
metadata tanpa mengubah file asli.

### 2.3 Satu Reusable Python Package

Seluruh logic yang digunakan oleh training, evaluation, dan inference
berada di:

``` text
src/parkindraw/
```

Backend tidak memiliki salinan model atau preprocessing sendiri.
Backend memanggil package `parkindraw.inference`.

### 2.4 Configuration over Hard-Coding

Path, hyperparameter, preprocessing, augmentation, threshold, dan fusion
method disimpan dalam file konfigurasi atau environment variable.

Secret tidak pernah disimpan dalam file konfigurasi yang masuk Git.

### 2.5 Artifact dan Report Memiliki Fungsi Berbeda

- `artifacts/` berisi output runtime dan diabaikan Git;
- `reports/` berisi hasil terpilih yang layak didokumentasikan;
- MLflow mencatat parameter, metrics, run, dan model artifact eksperimen.

### 2.6 Build Bertahap

Folder dibuat ketika fasenya mulai dikerjakan. Struktur target tidak
berarti semua komponen harus diimplementasikan sejak awal.

## 3. Struktur Target

``` text
parkindraw-ai/
│
├── README.md
├── LICENSE
├── CITATION.cff
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── .env.example
├── .pre-commit-config.yaml
├── docker-compose.yml
│
├── .github/
│   └── workflows/
│       ├── python-quality.yml
│       ├── backend-test.yml
│       └── frontend-test.yml
│
├── configs/
│   ├── data/
│   │   └── audit.yaml
│   ├── experiments/
│   │   ├── resnet18.yaml
│   │   └── optuna.yaml
│   └── deployment/
│       └── inference.yaml
│
├── data/
│   ├── raw/
│   │   └── newhandpd/
│   │       ├── HealthyCircle/
│   │       ├── HealthyMeander/
│   │       ├── HealthySpiral/
│   │       ├── PatientCircle/
│   │       ├── PatientMeander/
│   │       └── PatientSpiral/
│   ├── interim/
│   ├── processed/
│   └── metadata/
│       ├── images.csv
│       ├── audit_report.json
│       ├── duplicate_groups.csv
│       └── splits/
│           ├── fold_0.csv
│           ├── fold_1.csv
│           └── ...
│
├── research/
│   └── literature/
│       ├── articles/
│       ├── evidence.csv
│       └── search-query.txt
│
├── notebooks/
│   ├── 01_dataset_audit.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_preprocessing_analysis.ipynb
│   └── 04_experiment_analysis.ipynb
│
├── src/
│   └── parkindraw/
│       ├── __init__.py
│       ├── data/
│       │   ├── audit.py
│       │   ├── metadata.py
│       │   ├── dataset.py
│       │   └── splits.py
│       ├── preprocessing/
│       │   ├── transforms.py
│       │   └── augmentation.py
│       ├── models/
│       │   └── resnet18.py
│       ├── training/
│       │   ├── engine.py
│       │   ├── train.py
│       │   └── optimize.py
│       ├── evaluation/
│       │   ├── metrics.py
│       │   ├── evaluate.py
│       │   └── plots.py
│       ├── fusion/
│       │   └── average.py
│       ├── inference/
│       │   ├── artifact.py
│       │   └── predictor.py
│       ├── tracking/
│       │   └── mlflow.py
│       └── utils/
│           ├── logging.py
│           └── seed.py
│
├── tests/
│   ├── unit/
│   ├── data/
│   ├── integration/
│   ├── smoke/
│   └── conftest.py
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   └── routes/
│   │   │       ├── health.py
│   │   │       └── screening.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── lifespan.py
│   │   │   └── logging.py
│   │   ├── schemas/
│   │   │   ├── health.py
│   │   │   └── screening.py
│   │   ├── services/
│   │   │   └── screening.py
│   │   └── observability/
│   │       └── metrics.py
│   ├── tests/
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── providers/
│   │   │   └── router/
│   │   ├── features/
│   │   │   ├── drawing/
│   │   │   ├── screening/
│   │   │   └── results/
│   │   ├── shared/
│   │   │   ├── components/
│   │   │   ├── api/
│   │   │   ├── hooks/
│   │   │   ├── i18n/
│   │   │   └── types/
│   │   └── assets/
│   ├── public/
│   ├── tests/
│   ├── package.json
│   ├── package-lock.json
│   └── Dockerfile
│
├── artifacts/
│   ├── checkpoints/
│   ├── models/
│   ├── predictions/
│   └── temporary/
│
├── reports/
│   ├── figures/
│   ├── metrics/
│   └── model-cards/
│
├── scripts/
│   ├── audit-data.ps1
│   ├── optimize.ps1
│   ├── train-final.ps1
│   └── run-local.ps1
│
├── infra/
│   ├── mlflow/
│   └── monitoring/
│       ├── prometheus/
│       │   └── prometheus.yml
│       └── grafana/
│           ├── dashboards/
│           └── provisioning/
│
└── docs/
    ├── ARCHITECTURE.md
    ├── BRANDING.md
    ├── DATA_CARD.md
    ├── LITERATURE_REVIEW.md
    ├── MODEL_PLAN.md
    ├── PLAN.md
    └── PROJECT_STRUCTURE.md
```

Nama file pada struktur target adalah rancangan awal. File hanya dibuat
ketika memiliki tanggung jawab yang nyata; jangan membuat module kosong
sekadar untuk menyamai diagram.

## 4. Tanggung Jawab Folder

### 4.1 Root Configuration

#### `pyproject.toml`

Single source of truth untuk:

- metadata package Python;
- versi minimum Python;
- dependency groups `core`, `training`, `api`, dan `dev`;
- konfigurasi pytest, formatter, linter, dan type checker.

`requirements.txt` terpisah untuk ML dan backend tidak digunakan sebagai
sumber dependency utama.

#### `uv.lock`

Lock file untuk menghasilkan environment yang reproducible. File ini
dihasilkan oleh package manager dan masuk Git.

#### `.env.example`

Daftar environment variable yang dibutuhkan tanpa secret atau credential
asli.

### 4.2 `configs/`

Konfigurasi yang masuk Git dan dapat ditinjau sebagai bagian dari setiap
eksperimen.

- `data/`: aturan audit dan metadata;
- `experiments/`: konfigurasi frozen-backbone ResNet-18 dan Optuna;
- `deployment/`: threshold dan pemilihan artifact inference.

Konfigurasi tidak berisi password, token, atau credential storage.

### 4.3 `data/`

#### `data/raw/newhandpd/`

Salinan lokal dataset NewHandPD asli. Folder ini diabaikan Git atau
dikelola dengan data versioning setelah storage dan lisensinya jelas.

#### `data/interim/`

Output sementara yang masih dapat berubah selama audit atau persiapan
data.

#### `data/processed/`

Data turunan yang siap digunakan model apabila preprocessing tidak
dijalankan on-the-fly.

#### `data/metadata/`

Single source of truth untuk identitas dan validitas data:

- `images.csv`: filepath, class, subject ID, drawing type, dan checksum;
- `audit_report.json`: jumlah, resolusi, channel, dan error audit;
- `duplicate_groups.csv`: exact atau near-duplicate group;
- `splits/`: assignment subject dan duplicate group ke setiap fold.

Label tidak boleh ditentukan hanya dari nama file karena pola nama
`HealthyCircle` pada dataset aktual tidak konsisten.

Split harus mempertimbangkan `subject_id` dan duplicate group agar gambar
identik tidak tersebar antara training dan evaluation.

### 4.4 `research/`

Material penelitian pendukung, termasuk artikel, tabel ekstraksi bukti,
dan search query. Folder ini berbeda dari `docs/`, yang hanya berisi
dokumentasi proyek yang sudah diringkas dan dirawat.

Distribusi ulang PDF harus mengikuti hak akses dan lisensi sumber.

### 4.5 `notebooks/`

Notebook hanya digunakan untuk:

- audit interaktif;
- exploratory data analysis;
- visualisasi preprocessing;
- analisis hasil eksperimen.

Logic reusable harus dipindahkan ke package `parkindraw`. Notebook
mengimpor package tersebut, bukan memiliki implementasi produksi sendiri.

### 4.6 `src/parkindraw/`

Package Python utama yang dipakai oleh training dan backend.

#### `data/`

Audit dataset, metadata builder, dataset loader, dan subject-aware split.

#### `preprocessing/`

Transformasi deterministik dan augmentation training. Validation, test,
dan inference tidak menerima augmentation stokastik.

#### `models/`

Satu implementasi ImageNet-pretrained ResNet-18. Backbone selalu
dibekukan dan hanya classification head yang dilatih. Circle, Meander,
dan Spiral tidak memiliki salinan source model; perbedaannya ditentukan
melalui konfigurasi.

#### `training/`

Training loop untuk classification head, checkpointing, early stopping,
dan hyperparameter optimization dengan Optuna. Training from scratch,
partial-backbone fine-tuning, dan full-backbone fine-tuning tidak
diimplementasikan.

#### `evaluation/`

Accuracy, precision, recall/sensitivity, specificity, F1-score, ROC-AUC,
confusion matrix, calibration, dan plot evaluasi.

#### `fusion/`

Simple average probability fusion menggunakan prediction model yang
sudah tersedia. Weighted fusion dan meta-classifier tidak digunakan.

#### `inference/`

Satu entry point inference yang:

1. memuat artifact dan manifest;
2. menerapkan preprocessing yang sama dengan evaluation;
3. menjalankan model;
4. menerapkan fusion dan threshold bila diperlukan;
5. mengembalikan prediction result yang terstruktur.

#### `tracking/`

Integrasi MLflow tanpa mencampurkan detail tracking ke model atau
training loop.

### 4.7 `tests/`

- `unit/`: fungsi kecil seperti parser, metrics, dan fusion;
- `data/`: schema metadata, jumlah subjek, duplicate leakage, dan split;
- `integration/`: data loader sampai prediction;
- `smoke/`: memastikan konfigurasi dan artifact dapat dijalankan.

Test data leakage merupakan quality gate wajib:

``` text
subject(train) ∩ subject(test) = ∅
duplicate_group(train) ∩ duplicate_group(test) = ∅
```

### 4.8 `backend/`

FastAPI bertindak sebagai HTTP adapter, bukan tempat implementasi ML.

``` text
HTTP Request
↓
Schema Validation
↓
Screening Service
↓
parkindraw.inference
↓
HTTP Response
```

- `api/`: router dan endpoint;
- `core/`: settings, lifecycle, dan logging aplikasi;
- `schemas/`: kontrak request dan response;
- `services/`: orchestration use case;
- `observability/`: metrics HTTP dan inference.

Tidak ada `backend/app/ml/`. Model dan preprocessing berasal dari package
`parkindraw`.

### 4.9 `frontend/`

React + TypeScript menggunakan pengelompokan berbasis fitur:

- `app/`: bootstrap, providers, dan router;
- `features/drawing/`: canvas atau upload drawing;
- `features/screening/`: alur input dan submission;
- `features/results/`: probability, hasil screening, dan penjelasan;
- `shared/`: komponen, API client, hooks, i18n, dan type lintas fitur.

UI meminta tepat satu Circle, satu Meander, dan satu Spiral. Ketiga input
wajib diberi label dan divalidasi secara terpisah sebelum dikirim untuk
average fusion.

### 4.10 `artifacts/`

Output lokal yang dapat dibuat ulang:

- checkpoints;
- exported models;
- predictions;
- temporary files.

Seluruh isi folder diabaikan Git, kecuali file petunjuk yang memang
diperlukan. Artifact final dicatat dengan minimal:

- model version;
- MLflow run ID;
- data/split version;
- preprocessing configuration;
- classification threshold;
- metrics;
- checksum.

### 4.11 `reports/`

Berisi output terpilih untuk komunikasi dan dokumentasi, misalnya plot
final, ringkasan metrics, data card, dan model card. Berbeda dengan
`artifacts/`, sebagian isi `reports/` dapat masuk Git.

### 4.12 `scripts/`

Script tipis untuk developer workflow. Business logic tidak ditulis ulang
di sini; script hanya memanggil package atau command yang resmi.

### 4.13 `infra/`

Konfigurasi service pendukung:

- MLflow tracking server;
- Prometheus;
- Grafana.

Database runtime, MLflow run data, dan credential tidak masuk Git.

### 4.14 `docs/`

Dokumentasi proyek yang dirawat:

- arsitektur;
- branding;
- data card;
- kajian literatur;
- model plan;
- project plan dan phase gates;
- struktur repository.

## 5. Dependency Direction

Dependency utama harus bergerak ke core package:

``` text
frontend
   ↓ HTTP
backend
   ↓ Python import
parkindraw.inference
   ↓
preprocessing / models / fusion
```

Aturan:

- `src/parkindraw/` tidak mengimpor `backend/`;
- `src/parkindraw/` tidak mengimpor `frontend/`;
- backend boleh mengimpor package `parkindraw`;
- notebook dan script boleh mengimpor package `parkindraw`;
- frontend hanya berkomunikasi melalui API contract;
- training dan inference memakai implementasi preprocessing yang sama.

## 6. Aturan Version Control

### Masuk Git

- source code;
- konfigurasi tanpa secret;
- metadata dan split manifest yang aman didistribusikan;
- test;
- dokumentasi;
- selected reports;
- dependency lock file;
- infrastructure configuration.

### Tidak Masuk Git

- raw/interim/processed image data;
- checkpoints dan exported model binaries;
- MLflow runtime data dan database;
- environment file berisi secret;
- log, cache, build output, dan virtual environment;
- notebook checkpoint;
- frontend dependency dan build directory.

Kebijakan dataset dapat beralih ke DVC setelah remote storage, lisensi,
dan workflow kolaborasi ditentukan.

## 7. Command Convention

Setelah package diinstal dalam development mode, command dijalankan
melalui package, bukan melalui manipulasi `PYTHONPATH`.

Contoh konseptual:

``` bash
python -m parkindraw.data.audit --config configs/data/audit.yaml
python -m parkindraw.training.train --config configs/experiments/resnet18.yaml
python -m parkindraw.evaluation.evaluate --run-id <run-id>
```

Test:

``` bash
pytest
```

Backend:

``` bash
uvicorn backend.app.main:app --reload
```

## 8. Implementasi Bertahap

Roadmap, pekerjaan, deliverable, dan exit criteria setiap fase dikelola
di `docs/PLAN.md`. Dokumen ini hanya menetapkan folder yang mulai aktif
pada setiap fase agar tidak menjadi sumber roadmap kedua.

| Phase | Fokus | Folder utama |
|---|---|---|
| 0 | Repository foundation | root configuration, `docs/`, `research/`, `src/parkindraw/` |
| 1 | Reproducible data audit | `configs/data/`, `data/metadata/`, `src/parkindraw/data/`, `tests/data/` |
| 2 | Input protocol dan safe splits | `data/metadata/splits/`, data tests, protocol documentation |
| 3 | Fixed ResNet-18 pipeline | `preprocessing/`, `models/`, `training/`, `evaluation/`, `tracking/` |
| 4 | Optuna per drawing | `configs/experiments/`, `training/optimize.py`, MLflow artifacts |
| 5 | Evaluation dan fusion | `evaluation/`, `fusion/`, `reports/` |
| 6 | Inference dan MLOps | `inference/`, `configs/deployment/`, `infra/mlflow/` |
| 7 | FastAPI backend | `backend/` |
| 8 | React frontend | `frontend/` |
| 9 | Monitoring dan deployment | `infra/monitoring/`, `.github/workflows/`, Docker configuration |

Folder kosong tidak dibuat hanya untuk memenuhi tabel. Folder mulai
ditambahkan ketika fase terkait menghasilkan source, configuration,
test, atau dokumentasi nyata.

## 9. Kondisi Aktual dan Rencana Migrasi

Pada environment pengembangan saat ini, folder luar berfungsi sebagai
workspace dan folder dalam merupakan repository root:

``` text
D:\project\parkindraw-ai\          # workspace, bukan repository
├── dataset\                       # raw download sementara
├── literature-review\             # material riset sementara
└── parkindraw-ai\                  # repository root
    └── docs\
```

Migrasi yang direncanakan:

``` text
..\dataset\             → data\raw\newhandpd\
..\literature-review\   → research\literature\
```

Migrasi dilakukan pada langkah terpisah setelah target path diverifikasi.
Raw dataset hanya dipindahkan sebagai satu unit dan isi file tidak
dimodifikasi.

## 10. Repository Naming

Repository:

``` text
parkindraw-ai
```

Python import package:

``` python
import parkindraw
```

Product name:

**ParkinDraw**
