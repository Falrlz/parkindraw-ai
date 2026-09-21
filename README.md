# ParkinDraw AI

ParkinDraw is an end-to-end research and clinical screening system for AI-assisted Parkinson's disease detection using drawing movement analysis (Circle, Meander, and Spiral).

> **Disclaimer**: ParkinDraw is designed as an AI-assisted screening research tool, not as an autonomous diagnostic device or a substitute for clinical medical evaluation by certified neurologists.

---

## 1. Monorepo Structure

```text
parkindraw-ai/
├── ml/           # Machine Learning workspace (data prep, CV training, holdout evaluation)
├── backend/      # FastAPI screening & inference API service (planned)
├── frontend/     # Interactive clinical screening web interface (planned)
├── infra/        # Containerization, deployment, and monitoring (planned)
├── docs/         # Architecture design documents and project guides
├── research/     # Scientific literature review, dataset references, and notes
└── README.md     # Monorepo overview and root documentation
```

---

## 2. Machine Learning Quickstart

The core machine learning engine is self-contained under the [`ml/`](ml/README.md) directory.

```bash
cd ml

# 1. Install dependencies with uv
uv sync

# 2. Run automated test suite
uv run pytest

# 3. Run the end-to-end ML pipeline (Data Prep -> 3-Fold Training -> Holdout Eval)
uv run python -m pipelines.full_pipeline
```

Detailed ML documentation, pipeline arguments, and dataset placement instructions can be found in [`ml/README.md`](ml/README.md).

---

## 3. Project Roadmap & Status

| Area | Scope | Status |
|---|---|:---:|
| **Data Integrity** | Anomaly resolution, SHA-256 duplicate clustering, zero clinical leakage | ✅ Completed |
| **Model Training** | Frozen ResNet-18 multi-modality classifiers with 3-Fold Cross-Validation | ✅ Completed |
| **Model Evaluation** | Locked 20% patient holdout test set with clinical confusion matrices | ✅ Completed |
| **Experiment Tracking**| Centralized MLflow tracking database under `artifacts/tracking/` | ✅ Completed |
| **Backend API** | High-performance inference server using FastAPI | ⏳ Planned |
| **Frontend UI** | Responsive clinical drawing and screening web application | ⏳ Planned |
| **Deployment** | Docker containers and cloud infrastructure | ⏳ Planned |

---

## 4. License

ParkinDraw source code is licensed under the [MIT License](LICENSE). The NewHandPD dataset and third-party research literature retain their original terms and are not redistributed under this license.
