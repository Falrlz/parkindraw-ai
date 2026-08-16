"""Unit tests for persistent drawing-specific optimization orchestration."""

import json
from contextlib import contextmanager
from types import SimpleNamespace

import pytest
import yaml

from parkindraw.pipelines import optimization
from parkindraw.training.optimization_config import OptimizationConfig


def write_training_config(tmp_path):
    path = tmp_path / "training.yaml"
    path.write_text(
        yaml.safe_dump({"epochs": 2, "seed": 17, "device": "cpu"}),
        encoding="utf-8",
    )
    return path


def make_config(tmp_path, **overrides):
    settings = {
        "training_config": str(write_training_config(tmp_path)),
        "drawing_types": ("spiral",),
        "n_trials": 2,
        "study_db": str(tmp_path / "studies.db"),
        "output_dir": str(tmp_path / "summaries"),
        "pruner_startup_trials": 0,
    }
    settings.update(overrides)
    return OptimizationConfig(**settings)


def deterministic_objective(
    trial,
    base_config,
    optimization_config,
    drawing_type,
):
    value = trial.suggest_float("learning_rate", 1e-4, 1e-3, log=True)
    trial.set_user_attr("drawing_type", drawing_type)
    trial.set_user_attr(
        "fold_metrics",
        [{"fold": 0, "roc_auc": value, "accuracy": 0.7, "f1": 0.6}],
    )
    trial.set_user_attr("mean_roc_auc", value)
    return value


def test_pipeline_persists_summary_and_does_not_exceed_resumed_budget(
    monkeypatch,
    tmp_path,
):
    calls = []

    def counted_objective(*args, **kwargs):
        calls.append(args[3])
        return deterministic_objective(*args, **kwargs)

    monkeypatch.setattr(optimization, "evaluate_trial", counted_objective)
    config = make_config(tmp_path)

    first = optimization.run_optimization_pipeline(config)
    second = optimization.run_optimization_pipeline(config)

    assert calls == ["spiral", "spiral"]
    assert first.studies[0].trial_count == 2
    assert second.studies[0].trial_count == 2
    summary = json.loads(second.studies[0].summary_path.read_text())
    assert summary["objective"] == "mean_validation_subject_roc_auc"
    assert summary["base_training_config"]["epochs"] == 2
    assert summary["base_training_config"]["seed"] == 17
    assert len(summary["trials"]) == 2
    assert summary["best_trial"]["params"]["learning_rate"]


def test_pipeline_creates_a_separate_study_for_each_drawing(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(optimization, "evaluate_trial", deterministic_objective)
    config = make_config(
        tmp_path,
        drawing_types=("circle", "meander"),
        n_trials=1,
    )

    result = optimization.run_optimization_pipeline(config)

    assert [study.study_name for study in result.studies] == [
        "parkindraw-circle-head",
        "parkindraw-meander-head",
    ]
    assert all(study.trial_count == 1 for study in result.studies)
    assert (tmp_path / "summaries" / "circle.json").is_file()
    assert (tmp_path / "summaries" / "meander.json").is_file()


def test_pipeline_records_tracker_run_id_and_trial_outcome(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(optimization, "evaluate_trial", deterministic_objective)
    events = []

    class FakeTracker:
        def configure(self):
            events.append(("configure",))

        @contextmanager
        def start_run(self, name, settings):
            events.append(("start", name, settings))
            yield SimpleNamespace(info=SimpleNamespace(run_id="run-123"))
            events.append(("end",))

        def log_optimization_trial(self, trial, value, state):
            events.append(("result", trial.number, value, state))

    result = optimization.run_optimization_pipeline(
        make_config(tmp_path, n_trials=1),
        training_overrides={"epochs": 1},
        tracker=FakeTracker(),
    )

    assert [event[0] for event in events] == [
        "configure",
        "start",
        "result",
        "end",
    ]
    assert events[1][1] == "parkindraw-spiral-head-trial0"
    assert events[1][2]["base_epochs"] == 1
    assert events[2][3] == "complete"
    summary = json.loads(result.studies[0].summary_path.read_text())
    assert summary["trials"][0]["user_attrs"]["mlflow_run_id"] == "run-123"


def test_pipeline_reports_when_timeout_yields_no_completed_trial(
    monkeypatch,
    tmp_path,
):
    def pruned_objective(*args, **kwargs):
        raise optimization.optuna.TrialPruned()

    monkeypatch.setattr(optimization, "evaluate_trial", pruned_objective)

    with pytest.raises(optimization.OptimizationError, match="no completed trials"):
        optimization.run_optimization_pipeline(make_config(tmp_path, n_trials=1))


def test_resume_rejects_a_changed_study_definition(monkeypatch, tmp_path):
    monkeypatch.setattr(optimization, "evaluate_trial", deterministic_objective)
    optimization.run_optimization_pipeline(make_config(tmp_path, n_trials=1))

    with pytest.raises(optimization.OptimizationError, match="does not match"):
        optimization.run_optimization_pipeline(
            make_config(tmp_path, n_trials=2, dropout_high=0.4)
        )


def test_resume_rejects_a_budget_below_existing_trial_count(monkeypatch, tmp_path):
    monkeypatch.setattr(optimization, "evaluate_trial", deterministic_objective)
    optimization.run_optimization_pipeline(make_config(tmp_path, n_trials=2))

    with pytest.raises(optimization.OptimizationError, match="exceeds"):
        optimization.run_optimization_pipeline(make_config(tmp_path, n_trials=1))
