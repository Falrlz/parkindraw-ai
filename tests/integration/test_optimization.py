"""Integration coverage for Optuna persistence through the fold objective."""

import json

import yaml

from parkindraw.pipelines.optimization import run_optimization_pipeline
from parkindraw.training import optimize
from parkindraw.training.optimization_config import OptimizationConfig
from parkindraw.training.trainer import TrainingResult


def test_study_runs_real_fold_objective_and_publishes_reproducible_summary(
    monkeypatch,
    tmp_path,
):
    training_config = tmp_path / "training.yaml"
    training_config.write_text(
        yaml.safe_dump({"epochs": 1, "seed": 42, "device": "cpu"}),
        encoding="utf-8",
    )
    seen = []

    def fake_train(config):
        seen.append((config.drawing_type, config.fold, config.dropout))
        roc_auc = 0.65 + config.fold * 0.05 + config.dropout * 0.01
        return TrainingResult(
            config={},
            history=[
                {
                    "epoch": 1,
                    "train_loss": 0.5,
                    "validation_loss": 0.4,
                }
            ],
            best_epoch=1,
            best_metrics={"roc_auc": roc_auc, "accuracy": 0.7, "f1": 0.6},
        )

    monkeypatch.setattr(optimize, "train_fold", fake_train)
    config = OptimizationConfig(
        training_config=str(training_config),
        drawing_types=("circle",),
        n_trials=2,
        n_splits=3,
        study_db=str(tmp_path / "optuna.db"),
        output_dir=str(tmp_path / "reports"),
        pruner_startup_trials=2,
    )

    result = run_optimization_pipeline(config)

    assert len(seen) == 6
    assert {entry[0] for entry in seen} == {"circle"}
    assert [entry[1] for entry in seen] == [0, 1, 2, 0, 1, 2]
    summary = json.loads(result.studies[0].summary_path.read_text())
    assert len(summary["trials"]) == 2
    assert all(
        len(trial["user_attrs"]["fold_metrics"]) == 3
        for trial in summary["trials"]
    )
    assert summary["trials"][0]["user_attrs"]["fold_metrics"][0]["history"]
    assert summary["best_trial"]["value"] == result.studies[0].best_value
