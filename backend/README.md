# Parkindraw AI - Backend

This sub-project provides the high-performance REST API for **Parkindraw AI**, delivering automated AI-assisted clinical screening for Parkinson's disease based on handwriting drawing analysis (**Circle**, **Meander**, and **Spiral**).

The service is built on **FastAPI**, **Pydantic v2**, and **PyTorch**, employing a *Decoupled Serving* architecture that runs lightweight in-memory inference without runtime dependencies on the training pipeline package.

---

## Tech Stack

- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous ASGI REST API)
- **Data Validation & Settings**: [Pydantic v2](https://docs.pydantic.dev/) + `pydantic-settings`
- **Deep Learning Runtime**: [PyTorch](https://pytorch.org/) (CPU/CUDA inference) + [torchvision](https://pytorch.org/vision/)
- **Image Processing**: [Pillow](https://python-pillow.org/) (In-memory RGB validation & tensor preparation)
- **Server Gateway**: [Uvicorn](https://www.uvicorn.org/) (Standard ASGI worker)
- **Environment & Package Manager**: [uv](https://docs.astral.sh/uv/)

---

## Directory Structure

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
│   │   ├── common.py                # Enums (DrawingModality, PredictionClass) & error schemas
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

## Architecture & Key Features

### 1. Decoupled In-Memory Serving
The backend loads serialized PyTorch weights (`resnet18_circle.pt`, `resnet18_meander.pt`, `resnet18_spiral.pt`) into a singleton `ModelRegistry` upon application startup. Uploaded drawing files are processed strictly in RAM using `io.BytesIO` and Pillow, converted into normalized tensors (`[1, 3, 224, 224]`), and evaluated without persisting biometric data to disk or databases.

### 2. Late Multi-Modal Probability Fusion
When all three drawing tests are submitted in a single screening session, the backend performs modality-specific inference and calculates an aggregate risk score using equal-weighted probability averaging:

$$P_{\text{fusion}}(\text{Parkinson}) = \frac{P_{\text{circle}} + P_{\text{meander}} + P_{\text{spiral}}}{3}$$

The aggregate probability is evaluated against the configurable decision threshold (default: `0.50`) to produce the final screening classification.

### 3. API Endpoints Reference

#### A. Health and Readiness
- **`GET /health`** (or **`GET /api/v1/health`**)
  - Returns service status, active compute device (`cpu` or `cuda`), and model loading readiness flags.

#### B. Single Drawing Prediction
- **`POST /api/v1/predict/single`**
  - Form Data: `file` (image binary), `modality` (`circle`, `meander`, or `spiral`), and optional `threshold`.
  - Returns individual class prediction, confidence score, and probability distribution.

#### C. Complete Screening Session (Late Fusion)
- **`POST /api/v1/predict/session`**
  - Form Data: `circle_file`, `meander_file`, `spiral_file`, and optional `threshold`.
  - Executes simultaneous 3-modality evaluation, computes late fusion aggregate metrics, and returns session ID and modality breakdowns.

#### D. Model Specifications & Benchmark Metrics
- **`GET /api/v1/models/info`**
  - Delivers architectural details, input image requirements, and verified locked holdout test benchmark scores.

---

## Getting Started & Local Development

### 1. Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

### 2. Installation
From the `backend/` directory:
```bash
uv sync
```

### 3. Running the Server
```bash
# Option A: Run via uvicorn directly with hot reload
uv run uvicorn app.main:app --reload --port 8000

# Option B: Run via entrypoint script
uv run python main.py
```

### 4. Interactive API Documentation
Once running, explore and test the endpoints via interactive browser interfaces:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Quality Assurance & Testing

```bash
# Run unit and integration tests (14 passing tests)
uv run pytest

# Run code style and linting validation
uv run ruff check .
```

---

## License & Disclaimers

The Parkindraw backend codebase is licensed under the [MIT License](../LICENSE).
