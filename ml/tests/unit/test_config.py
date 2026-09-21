"""Tests for configuration and logging utilities."""

from pathlib import Path

from src.config.config import (
    ARTIFACTS_DIR,
    DEFAULT_CONFIG_PATH,
    FIGURES_DIR,
    MASTER_MANIFEST_PATH,
    ML_ROOT,
    MODELS_DIR,
    RAW_DATA_DIR,
    REPORTS_DIR,
    SPLITS_DIR,
    TRACKING_DIR,
    TRAIN_CONFIG_PATH,
    load_config,
    resolve_path,
)
from src.utils.logger import get_logger


def test_get_logger():
    logger = get_logger("test_module")
    assert logger.name == "test_module"
    assert len(logger.handlers) >= 1


def test_path_constants():
    assert ML_ROOT.is_dir()
    assert RAW_DATA_DIR == ML_ROOT / "data" / "raw"
    assert SPLITS_DIR == ML_ROOT / "data" / "splits"
    assert MASTER_MANIFEST_PATH == SPLITS_DIR / "master_manifest.csv"
    assert ARTIFACTS_DIR == ML_ROOT / "artifacts"
    assert MODELS_DIR == ARTIFACTS_DIR / "models"
    assert REPORTS_DIR == ARTIFACTS_DIR / "reports"
    assert FIGURES_DIR == REPORTS_DIR / "figures"
    assert TRACKING_DIR == ARTIFACTS_DIR / "tracking"
    assert TRAIN_CONFIG_PATH == ML_ROOT / "configs" / "experiments" / "resnet18.yaml"
    assert DEFAULT_CONFIG_PATH == TRAIN_CONFIG_PATH


def test_resolve_path():
    rel = Path("data/raw")
    resolved = resolve_path(rel)
    assert resolved == ML_ROOT / "data" / "raw"
    assert resolve_path(resolved) == resolved


def test_load_config_valid(tmp_path: Path):
    cfg_file = tmp_path / "test_config.yaml"
    cfg_file.write_text("batch_size: 64\nlearning_rate: 0.002\n", encoding="utf-8")
    loaded = load_config(cfg_file)
    assert loaded["batch_size"] == 64
    assert loaded["learning_rate"] == 0.002


def test_load_config_non_existent():
    loaded = load_config("non_existent_file.yaml")
    assert loaded == {}
