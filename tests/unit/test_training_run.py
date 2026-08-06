"""Characterization tests for the current training command-line workflow."""

from types import SimpleNamespace

import yaml

from parkindraw.training import run


def write_config(tmp_path, **settings):
    """Write the smallest useful training config for CLI tests."""
    path = tmp_path / "training.yaml"
    path.write_text(yaml.safe_dump(settings), encoding="utf-8")
    return path


def training_result():
    """Return a lightweight stand-in for a completed training run."""
    return SimpleNamespace(
        history=[{"epoch": 1, "accuracy": 0.75}],
        best_epoch=1,
        best_metrics={"accuracy": 0.75},
    )


def pipeline_result(checkpoint_dir, name, result=None):
    """Return the pipeline contract consumed by the current CLI."""
    return SimpleNamespace(
        run_name=name,
        checkpoint_path=checkpoint_dir / f"{name}.pt",
        training=result or training_result(),
    )


def test_parser_defaults_match_the_documented_local_command():
    args = run.build_argument_parser().parse_args([])

    assert args.config == run.DEFAULT_CONFIG
    assert args.checkpoint_dir == run.DEFAULT_CHECKPOINT_DIR
    assert args.drawing_type is None
    assert args.fold is None
    assert args.epochs is None
    assert args.batch_size is None
    assert args.seed is None
    assert args.device is None
    assert args.no_tracking is False


def test_parser_accepts_every_supported_override():
    args = run.build_argument_parser().parse_args(
        [
            "--config",
            "custom.yaml",
            "--drawing-type",
            "circle",
            "--fold",
            "2",
            "--epochs",
            "4",
            "--batch-size",
            "8",
            "--seed",
            "7",
            "--device",
            "cpu",
            "--checkpoint-dir",
            "custom-checkpoints",
            "--no-tracking",
        ]
    )

    assert vars(args) == {
        "config": "custom.yaml",
        "drawing_type": "circle",
        "fold": 2,
        "epochs": 4,
        "batch_size": 8,
        "seed": 7,
        "device": "cpu",
        "checkpoint_dir": "custom-checkpoints",
        "no_tracking": True,
    }


def test_load_config_preserves_yaml_values_when_overrides_are_none(tmp_path):
    path = write_config(tmp_path, drawing_type="meander", fold=1, epochs=6)

    config = run.load_config(path, drawing_type=None, fold=None, epochs=None)

    assert config.drawing_type == "meander"
    assert config.fold == 1
    assert config.epochs == 6


def test_main_without_tracking_only_trains_and_prints_result(
    monkeypatch,
    tmp_path,
    capsys,
):
    config_path = write_config(tmp_path, drawing_type="spiral", fold=2, epochs=1)
    checkpoint_dir = tmp_path / "checkpoints"
    calls = []

    def fake_pipeline(config, received_checkpoint_dir, *, tracker):
        calls.append((config, received_checkpoint_dir, tracker))
        return pipeline_result(checkpoint_dir, "spiral-fold2")

    monkeypatch.setattr(run, "run_training_pipeline", fake_pipeline)

    exit_code = run.main(
        [
            "--config",
            str(config_path),
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--no-tracking",
        ]
    )

    assert exit_code == 0
    assert len(calls) == 1
    config, received_checkpoint_dir, tracker = calls[0]
    assert config.drawing_type == "spiral"
    assert config.fold == 2
    assert received_checkpoint_dir == str(checkpoint_dir)
    assert tracker is None

    output = capsys.readouterr().out
    checkpoint = checkpoint_dir / "spiral-fold2.pt"
    assert "Run: spiral-fold2" in output
    assert "Best epoch: 1 of 1 run" in output
    assert '"accuracy": 0.75' in output
    assert f"Checkpoint: {checkpoint}" in output


def test_main_with_tracking_passes_mlflow_adapter_to_pipeline(
    monkeypatch,
    tmp_path,
):
    config_path = write_config(tmp_path, drawing_type="circle", fold=0, epochs=1)
    checkpoint_dir = tmp_path / "checkpoints"
    calls = []

    def fake_pipeline(config, received_checkpoint_dir, *, tracker):
        calls.append((config, received_checkpoint_dir, tracker))
        return pipeline_result(checkpoint_dir, "circle-fold0")

    monkeypatch.setattr(run, "run_training_pipeline", fake_pipeline)

    exit_code = run.main(
        [
            "--config",
            str(config_path),
            "--checkpoint-dir",
            str(checkpoint_dir),
        ]
    )

    assert exit_code == 0
    assert len(calls) == 1
    config, received_checkpoint_dir, tracker = calls[0]
    assert config.drawing_type == "circle"
    assert config.fold == 0
    assert received_checkpoint_dir == str(checkpoint_dir)
    assert tracker is run.mlflow_setup
