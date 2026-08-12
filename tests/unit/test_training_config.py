"""Unit tests for training configuration loading and validation."""

import dataclasses
from pathlib import Path

import pytest
import yaml

from parkindraw.training import trainer
from parkindraw.training.config import TrainingConfig, load_training_config


def write_config(tmp_path, settings) -> Path:
    path = tmp_path / "training.yaml"
    path.write_text(yaml.safe_dump(settings), encoding="utf-8")
    return path


def test_shipped_config_builds_the_training_dataclass():
    config = load_training_config("configs/experiments/resnet18.yaml")

    assert isinstance(config, TrainingConfig)


def test_overrides_take_precedence_except_when_they_are_none(tmp_path):
    path = write_config(tmp_path, {"drawing_type": "spiral", "epochs": 30})

    config = load_training_config(path, epochs=2, drawing_type=None)

    assert config.epochs == 2
    assert config.drawing_type == "spiral"


def test_unknown_config_keys_are_rejected(tmp_path):
    path = write_config(tmp_path, {"learning_rat": 0.1})

    with pytest.raises(ValueError, match="Unknown config keys"):
        load_training_config(path)


def test_non_mapping_yaml_is_rejected(tmp_path):
    path = write_config(tmp_path, ["spiral", 0])

    with pytest.raises(ValueError, match="must be a YAML mapping"):
        load_training_config(path)


def test_empty_yaml_uses_dataclass_defaults(tmp_path):
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")

    assert load_training_config(path) == TrainingConfig()


def test_every_dataclass_field_is_documented_in_the_shipped_yaml():
    text = Path("configs/experiments/resnet18.yaml").read_text(encoding="utf-8")
    shipped = yaml.safe_load(text)
    field_names = {field.name for field in dataclasses.fields(TrainingConfig)}

    assert set(shipped) == field_names


def test_original_trainer_config_remains_a_compatibility_import():
    assert trainer.TrainingConfig is TrainingConfig
