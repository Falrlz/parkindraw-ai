# ParkinDraw AI

**AI-assisted Parkinson's screening through drawing analysis.**

> **Disclaimer**: ParkinDraw is an AI-assisted screening tool, not a definitive medical diagnosis system or a substitute for professional clinical healthcare services.

---

## 📌 Overview

ParkinDraw is an end-to-end computer vision system designed for early Parkinson's Disease screening. By analyzing static handwriting and drawing patterns (**Circle**, **Meander**, and **Spiral**) from the **NewHandPD** dataset, ParkinDraw provides probability-based screening predictions.

## 🏗️ Architecture & Stack

- **Dataset**: NewHandPD (Healthy vs Parkinson)
- **Model**: Frozen-backbone ResNet-18 (classification head only)
- **Hyperparameter Optimization**: Optuna
- **Experiment Tracking**: MLflow
- **Core Package**: `src/parkindraw/` (Python)
- **Backend API**: FastAPI
- **Frontend App**: React + TypeScript
- **Monitoring**: Prometheus + Grafana

## 📁 Repository Structure

```text
parkindraw-ai/
├── configs/             # Experiment and data configs
├── data/                # Metadata, splits, and local raw dataset (git-ignored)
├── docs/                # Architecture, model plan, and project documentation
├── research/            # Literature review notes and evidence tables
├── src/
│   └── parkindraw/      # Reusable core Python package
├── backend/             # FastAPI backend API
├── frontend/            # React frontend web application
└── infra/               # MLflow & monitoring configuration
```

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- `uv` or `pip` package manager

### Environment Setup
```bash
# Install core package in editable mode
pip install -e .
```

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
