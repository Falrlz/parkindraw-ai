"""Tests for the bounded Optuna command-line entry point."""

from types import SimpleNamespace

import yaml
from scripts import optimize as cli


def write_config(tmp_path):
    path = tmp_path / "optuna.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "training_config": "training.yaml",
                "drawing_types": ["circle", "meander", "spiral"],
                "n_trials": 15,
            }
        ),
        encoding="utf-8",
    )
    return path


def test_parser_defaults_match_the_versioned_optimization_config():
    args = cli.build_argument_parser().parse_args([])

    assert args.config == cli.DEFAULT_CONFIG
    assert args.drawing_type is None
    assert args.n_trials is None
    assert args.timeout_seconds is None
    assert args.study_db is None
    assert args.output_dir is None
    assert args.epochs is None
    assert args.device is None
    assert args.no_tracking is False


def test_main_applies_overrides_and_can_disable_tracking(
    monkeypatch,
    tmp_path,
    capsys,
):
    config_path = write_config(tmp_path)
    summary_path = tmp_path / "spiral.json"
    calls = []

    def fake_pipeline(config, *, training_overrides, tracker):
        calls.append((config, training_overrides, tracker))
        return SimpleNamespace(
            studies=(
                SimpleNamespace(
                    study_name="parkindraw-spiral-head",
                    trial_count=2,
                    best_value=0.8123456,
                    best_params={"dropout": 0.2},
                    summary_path=summary_path,
                ),
            )
        )

    monkeypatch.setattr(cli, "run_optimization_pipeline", fake_pipeline)

    exit_code = cli.main(
        [
            "--config",
            str(config_path),
            "--drawing-type",
            "spiral",
            "--n-trials",
            "2",
            "--study-db",
            str(tmp_path / "study.db"),
            "--output-dir",
            str(tmp_path / "reports"),
            "--epochs",
            "1",
            "--device",
            "cpu",
            "--no-tracking",
        ]
    )

    assert exit_code == 0
    config, training_overrides, tracker = calls[0]
    assert config.drawing_types == ("spiral",)
    assert config.n_trials == 2
    assert config.study_db == str(tmp_path / "study.db")
    assert config.output_dir == str(tmp_path / "reports")
    assert training_overrides == {"epochs": 1, "device": "cpu"}
    assert tracker is None
    output = capsys.readouterr().out
    assert "Best validation ROC-AUC: 0.812346" in output
    assert '"dropout": 0.2' in output
    assert f"Summary: {summary_path}" in output


def test_main_enables_mlflow_by_default(monkeypatch, tmp_path):
    config_path = write_config(tmp_path)
    received = []

    def fake_pipeline(config, *, training_overrides, tracker):
        received.append(tracker)
        return SimpleNamespace(studies=())

    monkeypatch.setattr(cli, "run_optimization_pipeline", fake_pipeline)

    assert cli.main(["--config", str(config_path)]) == 0
    assert received == [cli.mlflow_setup]
