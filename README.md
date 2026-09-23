# ParkinDraw AI

ParkinDraw is an end-to-end research and clinical screening system for AI-assisted Parkinson's disease detection using drawing movement analysis (Circle, Meander, and Spiral).

> **Disclaimer**: ParkinDraw is designed as an AI-assisted screening research tool, not as an autonomous diagnostic device or a substitute for clinical medical evaluation by certified neurologists.

---

## 1. Monorepo Architecture

```text
parkindraw-ai/
├── ml/           # Machine Learning engine (data prep, CV training, holdout evaluation, MLflow)
├── backend/      # FastAPI screening & inference API service (decoupled serving, late fusion)
├── frontend/     # Interactive clinical screening web interface (React 19, TypeScript, Vite)
├── infra/        # Containerization, deployment configs, and monitoring (planned)
├── docs/         # Architecture design documents and project guides (local)
├── research/     # Scientific literature review, dataset references, and notes
└── README.md     # Monorepo overview and root documentation
```

---

## 2. Quickstart Guides

### 2.1 Machine Learning Engine (`ml/`)
The self-contained ML workspace trains and validates the deep learning classifiers:

```bash
cd ml

# 1. Install dependencies with uv
uv sync

# 2. Run automated test suite
uv run pytest

# 3. Execute the full end-to-end ML pipeline
uv run python -m pipelines.full_pipeline
```
*See [`ml/README.md`](ml/README.md) for detailed ML documentation, pipeline arguments, and dataset instructions.*

### 2.2 Backend API Service (`backend/`)
The high-performance REST API provides stateless in-memory inference and multi-modal late fusion:

```bash
cd backend

# 1. Install dependencies with uv
uv sync

# 2. Run automated test suite (14/14 passing)
uv run pytest

# 3. Start development server with hot-reload
uv run uvicorn app.main:app --reload --port 8000
```
*API documentation and interactive Swagger UI are available at `http://127.0.0.1:8000/docs`. See [`backend/README.md`](backend/README.md) for endpoint details.*

### 2.3 Frontend Web Application (`frontend/`)
The responsive clinical web application built with React 19, TypeScript, Vite, Tailwind CSS v4, Axios, and Lucide Icons:

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Start Vite development server
npm run dev
```
*Local development preview runs at `http://localhost:5173` with automated reverse-proxying to the FastAPI backend.*

---

## 3. Project Roadmap & Status

| Area | Scope | Status |
|---|---|:---:|
| **Data Integrity** | Anomaly resolution, SHA-256 duplicate clustering, zero clinical leakage | ✅ Completed |
| **Model Training** | Frozen ResNet-18 multi-modality classifiers with 3-Fold Cross-Validation | ✅ Completed |
| **Model Evaluation** | Locked 20% patient holdout test set with clinical confusion matrices | ✅ Completed |
| **Experiment Tracking**| Centralized MLflow tracking database under `ml/artifacts/tracking/` | ✅ Completed |
| **Backend API** | High-performance inference server using FastAPI with late fusion & pytest suite | ✅ Completed |
| **Frontend UI** | Responsive clinical drawing and screening web application (React 19 + Tailwind v4) | 🔄 In Progress |
| **Deployment** | Docker containers and cloud infrastructure | ⏳ Planned |

---

## 4. License

ParkinDraw source code is licensed under the [MIT License](LICENSE). The NewHandPD dataset and third-party research literature retain their original terms and are not redistributed under this license.
