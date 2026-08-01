# ParkinDraw AI

AI-assisted Parkinson's screening through Circle, Meander, and Spiral drawing
analysis.

> ParkinDraw is a research screening system, not a medical diagnosis or a
> substitute for professional clinical assessment.

## Project scope

ParkinDraw will train one ImageNet-pretrained ResNet-18 model per drawing type.
The backbone remains frozen, only the classification head is trained, and
Optuna is used for the bounded hyperparameter search. Application output is
the simple average of Circle, Meander, and Spiral probabilities.

Current phase:

| Phase | Scope | Status |
|---|---|---|
| 0 | Repository foundation | Implemented |
| 1 | Data governance and reproducible audit | Implemented; validated by quality gates |
| 2 | Leakage-safe dataset splits | Not started |
| 3+ | Training, evaluation, API, and application | Not started |

The detailed roadmap, data card, and learning guide are maintained locally
under `docs/`. This directory is intentionally excluded from Git.

## Repository structure

```text
parkindraw-ai/
├── configs/              # Versioned data and experiment configuration
├── data/
│   ├── raw/              # Local immutable dataset; ignored by Git
│   └── metadata/         # Reproducible audit manifests
├── docs/                 # Local project documentation; ignored by Git
├── notebooks/            # Exploration only; no production logic
├── research/             # Literature-review evidence
├── scripts/              # Thin operational helpers
├── src/parkindraw/       # Reusable Python package
└── tests/                # Unit, integration, and artifact-contract tests
```

Backend, frontend, infrastructure, and training implementation are added only
when their roadmap phase begins.

## Development setup

Prerequisites:

- Python 3.10–3.12;
- [uv](https://docs.astral.sh/uv/).

Install the package, Phase 1 data dependencies, and development tools:

```bash
uv sync --extra data --group dev
```

Training dependencies are intentionally separate because PyTorch, Optuna, and
MLflow are not required to run the data audit:

```bash
uv sync --extra data --extra train --group dev
```

EDA dependencies are also optional:

```bash
uv sync --extra data --extra eda --group dev
```

## Dataset placement and governance

Place the downloaded NewHandPD folders without renaming or modifying their
contents:

```text
data/raw/
├── HealthyCircle/
├── HealthyMeander/
├── HealthySpiral/
├── PatientCircle/
├── PatientMeander/
└── PatientSpiral/
```

The raw dataset is not covered by this repository's MIT license and must not be
committed or redistributed. Provenance, citation, and the unresolved source
license status are documented in the local `docs/DATA_CARD.md`.

## Data audit

Run the configuration-driven audit:

```bash
uv run --extra data parkindraw-audit --config configs/data/audit.yaml
```

Equivalent module command:

```bash
uv run --extra data python -m parkindraw.data.audit \
  --config configs/data/audit.yaml
```

The audit:

- fully decodes every supported image;
- parses class, subject, drawing type, and logical index;
- preserves raw filename tokens and records anomalies;
- computes SHA-256 and perceptual dHash;
- reports exact duplicates and near-duplicate candidates;
- validates expected image and subject counts;
- atomically publishes deterministic metadata artifacts.

The command is successful only when `data/metadata/audit_report.json` contains
`"status": "passed"`.

## Quality gates

```bash
uv run --extra data --group dev pytest
uv run --extra data --group dev ruff check src tests scripts notebooks
uv lock --check
git status --short
```

## License

ParkinDraw source code is licensed under the MIT License. See
[LICENSE](LICENSE). NewHandPD has separate, not-yet-explicitly-documented
source terms; see the Data Card before using or redistributing it.
