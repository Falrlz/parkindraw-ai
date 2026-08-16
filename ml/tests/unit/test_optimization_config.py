"""Unit tests for Optuna configuration loading and validation."""

import dataclasses
from pathlib import Path

import pytest
import yaml

from parkindraw.training.optimization_config import (
    MAX_TRIALS_PER_DRAWING,
    OptimizationConfig,
    load_optimization_config,
)


def write_config(tmp_path, settings) -> Path:
    path = tmp_path / "optuna.yaml"
    path.write_text(yaml.safe_dump(settings), encoding="utf-8")
    return path


def test_shipped_config_builds_the_optimization_dataclass():
    config = load_optimization_config("configs/experiments/optuna.yaml")

    assert isinstance(config, OptimizationConfig)
    assert config.drawing_types == ("circle", "meander", "spiral")
    assert config.batch_sizes == (8, 16, 32)


def test_overrides_take_precedence_except_when_they_are_none(tmp_path):
    path = write_config(tmp_path, {"n_trials": 15, "timeout_seconds": 60})

    config = load_optimization_config(path, n_trials=2, timeout_seconds=None)

    assert config.n_trials == 2
    assert config.timeout_seconds == 60


def test_unknown_keys_are_rejected(tmp_path):
    path = write_config(tmp_path, {"trial_count": 2})

    with pytest.raises(ValueError, match="Unknown optimization config keys"):
        load_optimization_config(path)


@pytest.mark.parametrize("n_trials", [0, MAX_TRIALS_PER_DRAWING + 1])
def test_trial_budget_is_bounded(n_trials):
    with pytest.raises(ValueError, match="n_trials must be between"):
        OptimizationConfig(n_trials=n_trials)


def test_unknown_drawing_type_is_rejected():
    with pytest.raises(ValueError, match="drawing_types must use"):
        OptimizationConfig(drawing_types=("spiral", "wave"))


def test_invalid_search_bounds_are_rejected():
    with pytest.raises(ValueError, match="dropout bounds"):
        OptimizationConfig(dropout_low=0.6, dropout_high=0.5)


def test_logarithmic_weight_decay_requires_a_positive_lower_bound():
    with pytest.raises(ValueError, match="weight-decay bounds"):
        OptimizationConfig(weight_decay_low=0.0)


def test_every_dataclass_field_is_documented_in_the_shipped_yaml():
    text = Path("configs/experiments/optuna.yaml").read_text(encoding="utf-8")
    shipped = yaml.safe_load(text)
    field_names = {field.name for field in dataclasses.fields(OptimizationConfig)}

    assert set(shipped) == field_names
