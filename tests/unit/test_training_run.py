"""Characterization tests for the current training command-line workflow."""

from contextlib import contextmanager
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

    def fake_train(config, checkpoint):
        calls.append((config, checkpoint))
        return training_result()

    def unexpected_tracking_call(*args, **kwargs):
        raise AssertionError("tracking must stay disabled")

    monkeypatch.setattr(run, "train_fold", fake_train)
    monkeypatch.setattr(run.mlflow_setup, "configure", unexpected_tracking_call)
    monkeypatch.setattr(run.mlflow_setup, "start_run", unexpected_tracking_call)
    monkeypatch.setattr(
        run.mlflow_setup,
        "log_training_result",
        unexpected_tracking_call,
    )

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
    config, checkpoint = calls[0]
    assert config.drawing_type == "spiral"
    assert config.fold == 2
    assert checkpoint == checkpoint_dir / "spiral-fold2.pt"

    output = capsys.readouterr().out
    assert "Run: spiral-fold2" in output
    assert "Best epoch: 1 of 1 run" in output
    assert '"accuracy": 0.75' in output
    assert f"Checkpoint: {checkpoint}" in output


def test_main_with_tracking_records_the_completed_run_in_order(
    monkeypatch,
    tmp_path,
):
    config_path = write_config(tmp_path, drawing_type="circle", fold=0, epochs=1)
    checkpoint_dir = tmp_path / "checkpoints"
    events = []

    def fake_configure():
        events.append(("configure",))

    @contextmanager
    def fake_start_run(name, config):
        events.append(("start", name, config))
        yield
        events.append(("end",))

    def fake_train(config, checkpoint):
        events.append(("train", config, checkpoint))
        return training_result()

    monkeypatch.setattr(run.mlflow_setup, "configure", fake_configure)
    monkeypatch.setattr(run.mlflow_setup, "start_run", fake_start_run)
    monkeypatch.setattr(
        run.mlflow_setup,
        "log_training_result",
        lambda result, path: events.append(("result", result, path)),
    )
    monkeypatch.setattr(run, "train_fold", fake_train)

    exit_code = run.main(
        [
            "--config",
            str(config_path),
            "--checkpoint-dir",
            str(checkpoint_dir),
        ]
    )

    assert exit_code == 0
    assert [event[0] for event in events] == [
        "configure",
        "start",
        "train",
        "result",
        "end",
    ]

    _, run_name, logged_config = events[1]
    assert run_name == "circle-fold0"
    assert logged_config["drawing_type"] == "circle"
    assert logged_config["fold"] == 0

    expected_checkpoint = checkpoint_dir / "circle-fold0.pt"
    assert events[2][2] == expected_checkpoint
    assert events[3][1].best_metrics == {"accuracy": 0.75}
    assert events[3][2] == expected_checkpoint
