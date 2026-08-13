"""Validated configuration for Optuna studies."""

from dataclasses import dataclass, fields
from pathlib import Path

import yaml

DRAWING_TYPES = ("circle", "meander", "spiral")
MAX_TRIALS_PER_DRAWING = 15


@dataclass(frozen=True)
class OptimizationConfig:
    """Search space, compute budget, persistence, and pruning policy."""

    training_config: str = "configs/experiments/resnet18.yaml"
    drawing_types: tuple[str, ...] = DRAWING_TYPES
    n_trials: int = MAX_TRIALS_PER_DRAWING
    timeout_seconds: float | None = None
    n_splits: int = 3
    study_seed: int = 42
    study_db: str | None = "artifacts/optuna.db"
    output_dir: str = "reports/optimization"
    learning_rate_low: float = 1e-5
    learning_rate_high: float = 1e-2
    weight_decay_low: float = 1e-6
    weight_decay_high: float = 1e-2
    dropout_low: float = 0.0
    dropout_high: float = 0.5
    dropout_step: float = 0.1
    batch_sizes: tuple[int, ...] = (8, 16, 32)
    pruner_startup_trials: int = 3
    pruner_warmup_steps: int = 1

    def __post_init__(self) -> None:
        unknown_drawings = set(self.drawing_types) - set(DRAWING_TYPES)
        if not self.drawing_types or unknown_drawings:
            raise ValueError(
                f"drawing_types must use {DRAWING_TYPES}; got {self.drawing_types}"
            )
        if len(set(self.drawing_types)) != len(self.drawing_types):
            raise ValueError("drawing_types must not contain duplicates")
        if not 1 <= self.n_trials <= MAX_TRIALS_PER_DRAWING:
            raise ValueError(
                f"n_trials must be between 1 and {MAX_TRIALS_PER_DRAWING}"
            )
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive or null")
        if self.n_splits < 2:
            raise ValueError("n_splits must be at least 2")
        if not 0 < self.learning_rate_low <= self.learning_rate_high:
            raise ValueError("learning-rate bounds must be positive and ordered")
        if not 0 < self.weight_decay_low <= self.weight_decay_high:
            raise ValueError("weight-decay bounds must be positive and ordered")
        if not 0 <= self.dropout_low <= self.dropout_high < 1:
            raise ValueError("dropout bounds must be ordered within [0, 1)")
        if self.dropout_step <= 0:
            raise ValueError("dropout_step must be positive")
        if not self.batch_sizes or any(size <= 0 for size in self.batch_sizes):
            raise ValueError("batch_sizes must contain positive integers")
        if self.pruner_startup_trials < 0 or self.pruner_warmup_steps < 0:
            raise ValueError("pruner settings must be non-negative")


def load_optimization_config(
    path: str | Path,
    **overrides: object,
) -> OptimizationConfig:
    """Load one optimization YAML and apply explicit, non-None overrides."""
    loaded = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if loaded is None:
        settings = {}
    elif isinstance(loaded, dict):
        settings = loaded.copy()
    else:
        raise ValueError("Optimization config must be a YAML mapping.")

    settings.update(
        {key: value for key, value in overrides.items() if value is not None}
    )
    known_fields = {field.name for field in fields(OptimizationConfig)}
    unknown_fields = set(settings) - known_fields
    if unknown_fields:
        raise ValueError(f"Unknown optimization config keys: {sorted(unknown_fields)}")

    if "drawing_types" in settings:
        settings["drawing_types"] = tuple(settings["drawing_types"])
    if "batch_sizes" in settings:
        settings["batch_sizes"] = tuple(settings["batch_sizes"])
    return OptimizationConfig(**settings)
