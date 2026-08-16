# ParkinDraw AI

ParkinDraw is an end-to-end research project for AI-assisted Parkinson's
screening through Circle, Meander, and Spiral drawing analysis.

> ParkinDraw is a research screening system, not a medical diagnosis or a
> substitute for professional clinical assessment.

## Monorepo structure

```text
parkindraw-ai/
├── frontend/   # React + TypeScript application (planned)
├── backend/    # FastAPI application (planned)
├── ml/         # Data preparation, experiments, training, and evaluation
├── infra/      # MLflow, monitoring, and deployment configuration
├── docs/       # Project-wide documentation
├── research/   # Literature review and research evidence
├── .github/    # Continuous-integration workflows
└── README.md   # Product-level documentation
```

The machine-learning project is self-contained under [`ml/`](ml/README.md).
Detailed project documentation is centralized under [`docs/`](docs/).
Literature-review materials are centralized under [`research/`](research/).
Run Python dependency, test, training, and optimization commands from that
directory:

```bash
cd ml
uv sync --extra data --extra train --group dev
uv run --extra data --extra train --group dev pytest
```

## Current status

| Area | Status |
|---|---|
| Data manifest and leakage-safe splits | Implemented |
| Metadata baseline and frozen ResNet-18 training | Implemented |
| Optuna workflow | Implemented; full studies pending |
| Fusion and inference package | Planned |
| FastAPI backend | Planned |
| React frontend | Planned |
| Monitoring and deployment | Planned |

Source code is licensed under the [MIT License](LICENSE). The NewHandPD
dataset and research articles have separate source terms and are not covered
by the repository license.
