"""Tests for the multi-drawing model training pipeline orchestrator."""

from pathlib import Path

from pipelines import train as train_pipeline
from pipelines.train import ALL_DRAWING_TYPES, load_config, main, run_training_pipeline


def test_load_config_valid(
    tmp_path: Path,
    ) -> None:

    """Verify loading valid YAML experiment configuration."""
    cfg_file = tmp_path / "test_config.yaml"
    cfg_file.write_text("epochs: 5\nbatch_size: 16\nlearning_rate: 0.005\n", encoding="utf-8")
    loaded = load_config(cfg_file)
    assert loaded["epochs"] == 5
    assert loaded["batch_size"] == 16
    assert loaded["learning_rate"] == 0.005


def test_load_config_non_existent(
    ) -> None:

    """Verify loading non-existent YAML configuration returns empty dict."""
    loaded = load_config("non_existent_file.yaml")
    assert loaded == {}


def test_all_drawing_types(
    ) -> None:

    """Verify supported drawing modality tuple."""
    assert ALL_DRAWING_TYPES == ("circle", "meander", "spiral")


def test_run_training_pipeline_orchestration(
    monkeypatch,
    ) -> None:

    """Verify run_training_pipeline correctly coordinates manifest and trainer."""
    calls = []

    def mock_load_config(path):
        return {"fold": "all", "epochs": 10}

    def mock_manifest(cfg):
        calls.append("manifest")
        return None

    def mock_trainer(master_manifest, cfg, drawing_types):
        calls.append(("train", drawing_types, cfg.get("fold")))
        return {"circle": {"metrics": {"accuracy": 0.88}}}

    monkeypatch.setattr(train_pipeline, "load_config", mock_load_config)
    monkeypatch.setattr(train_pipeline, "load_or_create_manifest", mock_manifest)
    monkeypatch.setattr(train_pipeline, "train_drawing_models", mock_trainer)

    results = run_training_pipeline(
        config_path="dummy.yaml",
        drawing_types=["circle"],
        overrides={"fold": "all"},
    )

    assert "manifest" in calls
    assert calls[1] == ("train", ["circle"], "all")
    assert "circle" in results


def test_main_cli_fold_parsing(
    monkeypatch,
    ) -> None:

    """Verify CLI parses fold all and integer fold properly."""
    captured_overrides = []

    def mock_run(config_path, drawing_types, overrides):
        captured_overrides.append(overrides)
        return {}

    monkeypatch.setattr(train_pipeline, "run_training_pipeline", mock_run)

    # 1. Test fold all
    main(["--fold", "all", "--drawing-type", "circle"])
    assert captured_overrides[-1]["fold"] == "all"

    # 2. Test fold 1
    main(["--fold", "1", "--drawing-type", "spiral"])
    assert captured_overrides[-1]["fold"] == 1
