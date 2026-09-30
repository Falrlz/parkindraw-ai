# Parkindraw AI

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.5%2B-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0%2B-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF.svg?logo=vite&logoColor=white)](https://vite.dev/)
[![Managed by uv](https://img.shields.io/badge/Managed%20by-uv-DE5FE9.svg?logo=astral&logoColor=white)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Draw. Analyze. Screen.**

Have you ever wondered if subtle changes in handwriting, minor hand tremors, or shaky drawing strokes could be early indicators of neuromotor impairment?

**Parkindraw AI** turns simple hand-drawn patterns into an accessible, non-invasive neuromotor screening tool. By analyzing three dynamic drawing tasks (**Circle**, **Meander**, and **Spiral**) using deep learning (ResNet-18) models and late multi-modal probability fusion, Parkindraw AI translates subtle movement irregularities into quantitative, easy-to-understand screening insights through an interactive bilingual dashboard.

---

## Preview

### Dashboard
![Dashboard](.github/assets/preview-dashboard.gif)

### Interactive Screening
![Interactive Screening](.github/assets/preview-screening.gif)

---

## What It Does

- **Multi-Modal Neuromotor Screening**: Guides participants through three standardized drawing protocols (Circle for circular trajectory stability, Meander for continuous wave coordination, and Spiral for Archimedean tremor detection).
- **Late Multi-Modal Probability Fusion**: Aggregates individual modality risk probabilities into a unified, calibrated decision score that significantly outperforms single-drawing evaluation.
- **Privacy-First In-Memory Processing**: Processes drawing vectors and image data purely in transient system RAM using `io.BytesIO`, ensuring sensitive biometric drawing records are never persisted to disk or external databases.
- **Bilingual Internationalization (i18n)**: Seamless client-side runtime switching between Indonesian (`id`) and English (`en`) across instructions, diagnostic tooltips, and clinical reports.
- **Decoupled Production Architecture**: Engineered as a modular monorepo cleanly isolating deep learning training workflows, high-throughput REST API serving, and a responsive presentation layer.

---

## How It Works

```text
[ Participant Drawing / Upload ]
               │
               ▼
[ 1. Digital Canvas Capture ] ──── In-memory binary blob generation via HTML5 Canvas
               │
               ▼
[ 2. REST API Ingestion ] ──────── FastAPI receives multipart/form-data payload
               │
               ▼
[ 3. Deterministic Preprocessing ] Resizing to 224x224, float tensor scaling, ImageNet normalization
               │
               ▼
[ 4. ResNet-18 Multi-Modality ] ── Simultaneous inference across Circle, Meander, and Spiral models
               │
               ▼
[ 5. Late Probability Fusion ] ── Equal-weighted probability averaging: P_fusion = (P_c + P_m + P_s) / 3
               │
               ▼
[ 6. Clinical Risk Report ] ────── Real-time risk tier classification and modality breakdown
```

### 1. Drawing Pattern Submission
The participant draws directly on an interactive touch/stylus-enabled HTML5 canvas or uploads scanned drawing files across three sequential examination steps.

### 2. In-Memory Preprocessing
Drawing inputs are received as binary streams and converted in RAM via Pillow into standardized $224 \times 224$ RGB tensors normalized to ImageNet distribution statistics ($\mu=[0.485, 0.456, 0.406], \sigma=[0.229, 0.224, 0.225]$).

### 3. Deep Learning Inference
The processed tensors are fed into three specialized ResNet-18 classifiers, each optimized to detect dysgraphic markers specific to its drawing geometry.

### 4. Late Fusion & Clinical Reporting
Individual modality probabilities are aggregated using late fusion to calculate the final composite risk score, returning an interactive clinical summary card, probability gauge, and per-modality metrics.

---

## Project Architecture

```text
parkindraw-ai/
├── frontend/                       # Interactive clinical web application
│   ├── public/                     # Static public assets
│   ├── src/
│   │   ├── app/                    # Layouts, client router, & Theme/Locale context providers
│   │   ├── components/             # Reusable design system primitives & shared components (Navbar, Footer)
│   │   ├── content/                # Decoupled bilingual copy (id/en) for all page views
│   │   ├── features/               # Feature modules (Screening wizard, HTML5 canvas, report cards)
│   │   ├── pages/                  # Page views (HomePage, ScreeningPage, AboutPage)
│   │   └── services/               # Axios API client & backend DTO interfaces
│   ├── package.json                # Frontend dependencies & npm scripts
│   └── vite.config.ts              # Vite configuration & backend proxy routing
│
├── backend/                        # FastAPI REST API & model serving engine
│   ├── app/
│   │   ├── api/v1/endpoints/       # Health checks, prediction endpoints, & model info
│   │   ├── core/                   # Application settings, CORS, & structured logging
│   │   ├── schemas/                # Pydantic validation models & response schemas
│   │   ├── services/               # Model loading, in-memory Pillow processing, predictor, & late fusion
│   │   └── main.py                 # FastAPI application factory & lifespan manager
│   ├── tests/                      # Automated API integration & unit tests (pytest + httpx)
│   ├── pyproject.toml              # Python dependencies & project configuration
│   └── main.py                     # Development server entrypoint script
│
├── ml/                             # Machine learning research & training pipeline
│   ├── configs/                    # Training hyperparameter configurations (resnet18.yaml)
│   ├── data/
│   │   ├── raw/                    # Raw NewHandPD drawing archives (Circle, Meander, Spiral)
│   │   └── splits/                 # Cluster-stratified master manifest (master_manifest.csv)
│   ├── notebooks/                  # Exploratory Data Analysis (EDA) notebooks
│   ├── pipelines/                  # End-to-end pipeline stages (preparation, train, evaluate)
│   ├── src/                        # Modular preprocessing, augmentation, ResNet-18, & evaluation
│   ├── artifacts/                  # Serialized weights, evaluation figures, & MLflow database
│   ├── tests/                      # Automated pipeline test suite (pytest)
│   └── pyproject.toml              # ML dependencies & uv environment lockfile
│
├── infra/                          # Cloud infrastructure, containerization, & CI/CD deployment (planned)
│   ├── docker/                     # Multi-stage Dockerfiles for backend and frontend (planned)
│   └── compose/                    # Multi-container orchestration configurations (planned)
│
├── docs/                           # Architecture specifications & project documentation
├── research/                       # Biomedical literature review & dataset notes
└── README.md                       # Master monorepo documentation
```

---

## Sub-System Architecture

### 1. Frontend Web Application (`frontend/`)
The frontend is built using **React 19**, **TypeScript**, **Vite 8**, and **Tailwind CSS v4**, delivering an accessible, medical-grade user experience:
- **Screening State Machine**: The `useScreeningSession` custom hook manages the multi-step screening lifecycle, retaining canvas drawing blobs in memory without data loss during step transitions.
- **Decoupled Copy & Localization**: Static text, clinical guidance, and educational FAQs are completely decoupled into `src/content/`, supporting instant runtime switching between Indonesian and English.
- **Visual Analytics**: Features dynamic SVG probability gauges, individual modality breakdown cards, and visual risk indicators with full light and dark mode support.

### 2. Backend API Service (`backend/`)
The backend is a high-performance asynchronous REST API built with **FastAPI**, **Pydantic v2**, and **PyTorch**:
- **Decoupled In-Memory Serving**: Loads serialized model weights into a singleton registry on startup, conducting inference without runtime dependencies on the training pipeline.
- **Late Multi-Modal Fusion**: Implements equal-weighted probability aggregation:
  $$P_{\text{fusion}}(\text{Parkinson}) = \frac{P_{\text{circle}} + P_{\text{meander}} + P_{\text{spiral}}}{3}$$
- **Interactive API Documentation**: Auto-generates interactive API playgrounds via Swagger UI (`/docs`) and ReDoc (`/redoc`).

### 3. Machine Learning Pipeline (`ml/`)
The machine learning pipeline handles dataset processing, model training, and experiment tracking:
- **Cluster-Aware Partitioning**: Groups identical image files via SHA-256 duplicate clustering to ensure connected subjects do not cross between training folds and the holdout test set.
- **Transfer Learning with ResNet-18**: Uses pre-trained ResNet-18 feature extractors with custom classification heads, trained using AdamW, early stopping, and ReduceLROnPlateau scheduling.
- **Stroke-Preserving Augmentation**: Applies mild affine adjustments (rotation within $\pm 5.0^\circ$, translation within $\pm 4\%$, scaling $0.95 - 1.05$) with paper-white borders, avoiding horizontal or vertical flips to maintain stroke trajectory.
- **Experiment Tracking**: Logs training metrics, validation curves, and model checkpoints to a local SQLite-backed MLflow server.

### 4. Infrastructure & Deployment (`infra/` - Planned)
Designed for upcoming production containerization and deployment workflows:
- **Containerized Serving**: Multi-stage Dockerfiles for packaging the FastAPI backend service and building the static frontend distribution via Nginx.
- **Service Orchestration**: Docker Compose configurations to orchestrate frontend, backend, and the MLflow experiment database within an isolated network.
- **CI/CD Quality Gates**: Automated continuous integration workflows for running lint checks, static type audits, and test suites across all sub-projects.

---

## Dataset & Clinical Benchmark Results

The models are trained and benchmarked on the **NewHandPD (New Hand Parkinson's Disease)** dataset, consisting of digitized drawing samples from clinical Parkinson's disease patients and healthy control subjects.

### 1. Dataset Partitioning Protocol

| Drawing Modality | Drawings / Subject | Development Set (80%) | Locked Holdout Set (20%) | Total Images |
| :--- | :---: | :---: | :---: | :---: |
| **Circle** | 1 | 53 | 13 | 66 |
| **Meander** | 4 | 212 | 52 | 264 |
| **Spiral** | 4 | 212 | 52 | 264 |
| **Total** | **9** | **477 (53 subjects)** | **117 (13 subjects)** | **594** |

The 117 holdout test images (13 subjects) remained completely unobserved during cross-validation training and hyperparameter selection, serving exclusively as an independent clinical benchmark.

### 2. Locked Holdout Test Evaluation Benchmark

| Drawing Modality | Test Support | Accuracy | Precision | Recall (Sensitivity) | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Circle** | 13 | **92.31%** | 85.71% | **100.00%** | **0.9231** | **0.9762** |
| **Meander** | 52 | **88.46%** | 82.14% | **95.83%** | **0.8846** | **0.9360** |
| **Spiral** | 52 | **88.46%** | 80.00% | **100.00%** | **0.8889** | **0.9911** |
| **Macro Average** | **117** | **89.74%** | **82.62%** | **98.61%** | **0.8989** | **0.9678** |

- **Test Recall**: Both Circle and Spiral models achieved **100.00% Recall** on the holdout partition, while Meander achieved **95.83% Recall**.
- **AUC-ROC Performance**: ROC-AUC scores exceeded **0.93** across all individual modalities (Spiral reaching **0.9911**), showing class separation between healthy control and Parkinsonian drawing samples on this dataset.

---

## Technology Stack

### Frontend
- **Framework**: React 19, TypeScript
- **Tooling & Bundler**: Vite 8
- **Styling**: Tailwind CSS v4 (`@tailwindcss/vite`)
- **Typography**: Figtree Variable Font
- **Icons**: Lucide React
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI (Asynchronous ASGI REST API)
- **Validation**: Pydantic v2, `pydantic-settings`
- **Inference Runtime**: PyTorch, torchvision
- **Image Processing**: Pillow (In-memory RGB validation)
- **Server Gateway**: Uvicorn
- **Environment**: Python 3.12+, Astral uv

### Machine Learning
- **Deep Learning**: PyTorch, torchvision (ResNet-18)
- **Experiment Tracking**: MLflow (SQLite backend)
- **Scientific Computing**: NumPy, Pandas, Scikit-Learn
- **Visualization**: Matplotlib, Seaborn

---

## Quick Start

### 1. Prerequisites
- **Python**: 3.12+
- **Node.js**: v18+ or v20+
- **Package Managers**: [uv](https://docs.astral.sh/uv/) (Python) and `npm` (Node.js)

### 2. Clone the Repository
```bash
git clone https://github.com/Falrlz/parkindraw-ai.git
cd parkindraw-ai
```

### 3. Run the Backend API Service
From the repository root:
```bash
cd backend

# Install dependencies using uv
uv sync

# Run tests
uv run pytest

# Start development server
uv run uvicorn app.main:app --reload --port 8000
```
Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

### 4. Run the Frontend Web Application
In a separate terminal:
```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open your browser and navigate to `http://localhost:5173/`.

### 5. Run ML Pipelines & MLflow Dashboard (Optional)
To inspect the ML models or launch experiment tracking:
```bash
cd ml

# Install ML dependencies
uv sync

# Run full ML pipeline (Data Prep -> 3-Fold CV -> Holdout Evaluation)
uv run python -m pipelines.full_pipeline --epochs 50 --batch-size 32

# Launch the MLflow tracking dashboard
uv run python -m mlflow ui --backend-store-uri sqlite:///artifacts/tracking/mlflow.db
```
The dashboard is accessible at `http://127.0.0.1:5000`.

---

## Acknowledgements

This project builds upon public biomedical datasets and published research on Parkinsonian motor dysfunction analysis:

- **Dataset**: [NewHandPD / HandPD Dataset Repository](https://wwwp.fc.unesp.br/~papa/pub/datasets/Handpd/) hosted by the Department of Computing, São Paulo State University (UNESP), Bauru, Brazil.
- **Primary Research Publication**:
  - Pereira, C. R., Weber, S. A. T., Hook, C., Rosa, G. H., & Papa, J. P. *"Deep Learning-Aided Parkinson's Disease Diagnosis from Handwritten Dynamics."* In 2016 29th SIBGRAPI Conference on Graphics, Patterns and Images (SIBGRAPI), pp. 340-346, 2016. DOI: [10.1109/SIBGRAPI.2016.054](https://doi.org/10.1109/SIBGRAPI.2016.054).

---

## Disclaimer

Parkindraw was developed for academic, research, and educational purposes as an AI-assisted screening tool and is **not** a certified medical diagnostic device. It should not be used as a substitute for professional medical advice, diagnosis, or clinical evaluation by certified physicians.

---

## License

Parkindraw source code is licensed under the [MIT License](LICENSE). The NewHandPD dataset and third-party academic literature retain their original terms and copyrights.
