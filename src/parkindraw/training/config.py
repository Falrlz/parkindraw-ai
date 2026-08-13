"""Training configuration definition and YAML loading."""

from dataclasses import dataclass, fields
from pathlib import Path

import yaml


@dataclass
class TrainingConfig:
    """Every setting that changes a run and must be recorded with its result."""

    drawing_type: str = "spiral"
    fold: int = 0
    epochs: int = 30
    batch_size: int = 32
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    dropout: float = 0.0
    early_stopping_patience: int = 5
    seed: int = 42
    device: str = "auto"
    num_workers: int = 0
    raw_dir: str = "data/raw"
    splits_dir: str = "data/splits"


def load_training_config(
    path: str | Path,
    **overrides: object,
) -> TrainingConfig:
    """Load YAML settings and apply explicit, non-None overrides."""
    loaded = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if loaded is None:
        settings = {}
    elif isinstance(loaded, dict):
        settings = loaded.copy()
    else:
        raise ValueError("Training config must be a YAML mapping.")

    settings.update(
        {key: value for key, value in overrides.items() if value is not None}
    )

    known_fields = {field.name for field in fields(TrainingConfig)}
    unknown_fields = set(settings) - known_fields
    if unknown_fields:
        raise ValueError(f"Unknown config keys: {sorted(unknown_fields)}")

    return TrainingConfig(**settings)
