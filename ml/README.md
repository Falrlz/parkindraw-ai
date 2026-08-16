# ParkinDraw ML

Machine-learning workspace for ParkinDraw's AI-assisted Parkinson's screening
research. Run every command in this document from `parkindraw-ai/ml/`.

> This is a research screening system, not a medical diagnosis or a substitute
> for professional clinical assessment.

## Scope and status

ParkinDraw trains one ImageNet-pretrained ResNet-18 model per drawing type. The
backbone remains frozen, only the classification head is trained, and Optuna
performs a bounded hyperparameter search. The planned application output is the
simple average of Circle, Meander, and Spiral probabilities.

| Phase | Scope | Status |
|---|---|---|
| 0 | Repository foundation and data audit | Implemented |
| 1 | Leakage-safe subject splits | Implemented; input protocol pending |
| 2 | Metadata baseline and fixed ResNet-18 pipeline | Implemented |
| 3 | Optuna studies per drawing type | Workflow implemented; full studies pending |
| 4+ | Fusion, inference, API, and application | Planned |

## Directory structure

```text
ml/
├── configs/              # Versioned experiment/deployment configuration
├── data/
│   ├── raw/              # Immutable local NewHandPD archive; ignored by Git
│   └── splits/           # Subject, fold, and session assignments
├── notebooks/            # Exploration only; no production logic
├── scripts/              # Thin command-line adapters
├── src/parkindraw/       # Reusable Python package
├── tests/                # Unit and integration tests
├── artifacts/            # Regenerable checkpoints and Optuna databases
├── reports/              # Selected reproducible reports
├── pyproject.toml        # Python package and tool configuration
└── uv.lock               # Reproducible dependency lock
```

Project-wide documentation and literature-review materials are centralized in
the sibling [`../docs/`](../docs/) and [`../research/`](../research/)
directories. The `../backend/`, `../frontend/`, and `../infra/` workspaces are
expanded when their roadmap phases begin.

## Workflow boundaries

```text
scripts/                     CLI arguments and terminal presentation
    ↓
src/parkindraw/pipelines/    End-to-end use-case orchestration
    ↓
data / training / models / evaluation

pipelines → tracking/        Optional MLflow adapter
```

Core modules do not parse command-line arguments or print terminal output.
MLflow API calls remain inside `src/parkindraw/tracking/`, and training can run
without tracking.

## Setup

Prerequisites:

- Python 3.10–3.12;
- [uv](https://docs.astral.sh/uv/).

Install data, training, and development dependencies:

```bash
uv sync --extra data --extra train --group dev
```

EDA dependencies are optional:

```bash
uv sync --extra data --extra eda --group dev
```

## Dataset placement

Place the NewHandPD folders under `data/raw/` without renaming or modifying
their contents:

```text
data/raw/
├── HealthyCircle/
├── HealthyMeander/
├── HealthySpiral/
├── PatientCircle/
├── PatientMeander/
└── PatientSpiral/
```

The dataset is not covered by the repository's MIT license and must not be
committed or redistributed without permission from its source.

## Commands

Create leakage-safe subject splits:

```bash
uv run --extra data --extra train python scripts/create_splits.py
```

Evaluate the metadata-only baseline:

```bash
uv run --extra data --extra train python scripts/evaluate_baseline.py
```

Train one drawing type and fold with MLflow tracking:

```bash
uv run --extra data --extra train python scripts/train.py \
  --config configs/experiments/resnet18.yaml \
  --drawing-type spiral \
  --fold 0
```

Run a one-epoch CPU check without tracking:

```bash
uv run --extra data --extra train python scripts/train.py \
  --epochs 1 \
  --device cpu \
  --no-tracking
```

Run or resume the bounded Optuna studies:

```bash
uv run --extra data --extra train python scripts/optimize.py \
  --config configs/experiments/optuna.yaml
```

Each drawing type has an independent persistent study. Re-running the command
only fills the remaining trials up to the configured total budget.

## Outputs

- subject assignments and sessions: `data/splits/`;
- selected checkpoints: `artifacts/checkpoints/`;
- persistent Optuna database: `artifacts/optuna.db`;
- MLflow database and artifacts: `mlflow.db`, `mlruns/`;
- metadata baseline: `reports/metadata_baseline.*`;
- optimization summaries: `reports/optimization/`.

Model selection and hyperparameter decisions use development folds only. The
locked holdout remains untouched until all training decisions are fixed.

## Quality gates

```bash
uv run --extra data --extra train --group dev pytest
uv run --extra data --extra train --group dev ruff check src tests scripts notebooks
uv lock --check
git status --short
```

## License

ParkinDraw source code is licensed under the MIT License. See
[`../LICENSE`](../LICENSE). NewHandPD and the research PDFs have separate source
terms.
