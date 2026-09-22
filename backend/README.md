# ParkinDraw AI --- Backend API Service

This sub-project provides the high-performance REST API for **ParkinDraw AI**, delivering automated AI-assisted clinical screening for Parkinson's disease based on handwriting drawing analysis (**Circle**, **Meander**, and **Spiral**).

The service is built on **FastAPI**, **Pydantic v2**, and **PyTorch**, employing a *Decoupled Serving* architecture that runs lightweight in-memory inference without runtime dependencies on the training pipeline package.

> **Clinical Research Disclaimer**: ParkinDraw is designed as an AI-assisted clinical screening research tool. It is not an autonomous diagnostic medical device or a replacement for clinical neurological examination by board-certified physicians.

---

## Architecture Overview

```text
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── health.py        # GET /health, GET /api/v1/health
│   │   │   │   ├── predict.py       # POST /api/v1/predict/single, POST /api/v1/predict/session
│   │   │   │   └── models.py        # GET /api/v1/models/info
│   │   │   └── api.py               # API v1 router aggregator
│   ├── core/
│   │   ├── config.py                # Pydantic Settings (CORS, models directory, threshold)
│   │   └── logging.py               # Standardized structured system logging
│   ├── schemas/
│   │   ├── common.py                # Enums (DrawingModality, PredictionClass) & error schema
│   │   ├── health.py                # HealthResponse & ModelStatus
│   │   ├── prediction.py            # DrawingPrediction, SessionPredictionResponse
│   │   └── models_info.py           # Model specifications & holdout benchmark metrics
│   ├── services/
│   │   ├── model_loader.py          # Decoupled ResNet-18 architecture & singleton ModelRegistry
│   │   ├── image_processor.py       # In-memory Pillow validation, 224x224 resize, ImageNet normalization
│   │   ├── predictor.py             # Forward inference pass & softmax computation
│   │   └── fusion.py                # Simple Average Late Multi-Modal Fusion
│   └── main.py                      # FastAPI application factory, CORS, and lifespan manager
├── tests/                           # Comprehensive automated test suite (pytest + httpx)
├── pyproject.toml                   # Project dependencies and tool configurations
└── main.py                          # Development server entrypoint script
```

---

## API Endpoints Reference

### 1. Health & Readiness Check
* **`GET /health`** (or **`GET /api/v1/health`**)
  * Returns system readiness, active compute device (`cuda` or `cpu`), and model load status:
  ```json
  {
    "status": "ok",
    "version": "0.1.0",
    "environment": "development",
    "timestamp": "2026-09-22T14:30:00Z",
    "device": "cpu",
    "models": {
      "circle": true,
      "meander": true,
      "spiral": true
    },
    "all_models_loaded": true
  }
  ```

### 2. Single Drawing Prediction
* **`POST /api/v1/predict/single`**
  * Form Data Parameters:
    * `file`: Uploaded drawing image (`multipart/form-data`, PNG/JPG/WebP).
    * `modality`: Drawing type (`circle`, `meander`, or `spiral`).
    * `threshold`: *(Optional)* Custom decision threshold (default: `0.50`).
  * Example Response:
  ```json
  {
    "prediction": {
      "modality": "spiral",
      "prediction": "Parkinson",
      "prediction_code": 1,
      "confidence": 0.9425,
      "probabilities": {
        "Healthy": 0.0575,
        "Parkinson": 0.9425
      }
    },
    "clinical_disclaimer": "ParkinDraw is an AI-assisted screening research tool...",
    "timestamp": "2026-09-22T14:30:00Z"
  }
  ```

### 3. Complete Screening Session (Late Multi-Modal Fusion)
* **`POST /api/v1/predict/session`**
  * Evaluates all three drawings simultaneously and computes an aggregate score:
    $$P_{\text{fusion}}(\text{Parkinson}) = \frac{P_{\text{circle}} + P_{\text{meander}} + P_{\text{spiral}}}{3}$$
  * Form Data Parameters:
    * `circle_file`: Circle test image.
    * `meander_file`: Meander wave image.
    * `spiral_file`: Spiral drawing image.
    * `threshold`: *(Optional)* Custom screening threshold (default: `0.50`).
  * Example Response:
  ```json
  {
    "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "fusion_prediction": "Parkinson",
    "fusion_prediction_code": 1,
    "fusion_probability": 0.8950,
    "threshold": 0.50,
    "drawings": {
      "circle": { ... },
      "meander": { ... },
      "spiral": { ... }
    },
    "clinical_disclaimer": "ParkinDraw is an AI-assisted screening research tool...",
    "timestamp": "2026-09-22T14:30:00Z"
  }
  ```

### 4. Model Metadata & Holdout Benchmarks
* **`GET /api/v1/models/info`**
  * Delivers architectural specifications and verified locked holdout test benchmark scores.

---

## Local Development & Execution

### Prerequisites
* Python 3.12+
* [uv](https://docs.astral.sh/uv/)

### 1. Launch the API Server
Run from the `backend/` directory:

```powershell
# Option A: Run via uvicorn directly
uv run uvicorn app.main:app --reload --port 8000

# Option B: Run via entrypoint script
uv run python main.py
```

Access the interactive API documentation in your browser:
* **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Testing & Quality Assurance

Run the automated test suite and linter:

```powershell
# 1. Run all unit and integration tests
uv run pytest

# 2. Run Ruff code quality and style check
uv run ruff check .
```
