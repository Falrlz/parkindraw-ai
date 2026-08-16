"""Characterization tests for the local MLflow adapter."""

from contextlib import contextmanager
from types import SimpleNamespace

from parkindraw.tracking import mlflow_setup


def test_configure_creates_storage_and_selects_existing_experiment(
    monkeypatch,
    tmp_path,
):
    tracking_db = tmp_path / "tracking" / "mlflow.db"
    artifact_dir = tmp_path / "artifacts"
    calls = []

    monkeypatch.setattr(
        mlflow_setup.mlflow,
        "set_tracking_uri",
        lambda uri: calls.append(("tracking_uri", uri)),
    )
    monkeypatch.setattr(
        mlflow_setup.mlflow,
        "get_experiment_by_name",
        lambda name: calls.append(("get_experiment", name)) or object(),
    )
    monkeypatch.setattr(
        mlflow_setup.mlflow,
        "create_experiment",
        lambda *args, **kwargs: calls.append(("create_experiment", args, kwargs)),
    )
    monkeypatch.setattr(
        mlflow_setup.mlflow,
        "set_experiment",
        lambda name: calls.append(("set_experiment", name)),
    )

    mlflow_setup.configure(tracking_db, artifact_dir, "test-experiment")

    assert artifact_dir.is_dir()
    assert calls == [
        ("tracking_uri", f"sqlite:///{tracking_db.resolve().as_posix()}"),
        ("get_experiment", "test-experiment"),
        ("set_experiment", "test-experiment"),
    ]


def test_configure_creates_missing_experiment(monkeypatch, tmp_path):
    artifact_dir = tmp_path / "artifacts"
    created = []

    monkeypatch.setattr(mlflow_setup.mlflow, "set_tracking_uri", lambda uri: None)
    monkeypatch.setattr(
        mlflow_setup.mlflow,
        "get_experiment_by_name",
        lambda name: None,
    )
    monkeypatch.setattr(
        mlflow_setup.mlflow,
        "create_experiment",
        lambda name, artifact_location: created.append((name, artifact_location)),
    )
    monkeypatch.setattr(mlflow_setup.mlflow, "set_experiment", lambda name: None)

    mlflow_setup.configure(tmp_path / "mlflow.db", artifact_dir, "new-experiment")

    assert created == [("new-experiment", artifact_dir.resolve().as_uri())]


def test_start_run_logs_config_before_yielding(monkeypatch):
    events = []
    active_run = object()

    @contextmanager
    def fake_mlflow_run(run_name):
        events.append(("start", run_name))
        yield active_run
        events.append(("end",))

    monkeypatch.setattr(mlflow_setup.mlflow, "start_run", fake_mlflow_run)
    monkeypatch.setattr(
        mlflow_setup.mlflow,
        "log_params",
        lambda config: events.append(("params", config)),
    )

    with mlflow_setup.start_run("spiral-fold0", {"seed": 42}) as active:
        assert active is active_run
        events.append(("body",))

    assert events == [
        ("start", "spiral-fold0"),
        ("params", {"seed": 42}),
        ("body",),
        ("end",),
    ]


def test_log_history_records_only_numeric_epoch_metrics(monkeypatch):
    logged = []
    monkeypatch.setattr(
        mlflow_setup.mlflow,
        "log_metric",
        lambda key, value, step=None: logged.append((key, value, step)),
    )

    mlflow_setup.log_history(
        [
            {
                "epoch": 3,
                "train_loss": 0.25,
                "accuracy": 0.75,
                "note": "validation",
                "roc_auc": None,
            }
        ]
    )

    assert logged == [
        ("train_loss", 0.25, 3),
        ("accuracy", 0.75, 3),
    ]


def test_log_best_prefixes_numeric_metrics(monkeypatch):
    logged = []
    monkeypatch.setattr(
        mlflow_setup.mlflow,
        "log_metric",
        lambda key, value: logged.append((key, value)),
    )

    mlflow_setup.log_best(
        {
            "accuracy": 0.8,
            "roc_auc": None,
            "confusion_matrix": [[2, 1], [0, 3]],
        },
        best_epoch=4,
    )

    assert logged == [("best_epoch", 4), ("best_accuracy", 0.8)]


def test_log_checkpoint_only_logs_an_existing_file(monkeypatch, tmp_path):
    logged = []
    monkeypatch.setattr(
        mlflow_setup.mlflow,
        "log_artifact",
        lambda path: logged.append(path),
    )
    missing = tmp_path / "missing.pt"
    checkpoint = tmp_path / "model.pt"
    checkpoint.write_bytes(b"checkpoint")

    mlflow_setup.log_checkpoint(missing)
    mlflow_setup.log_checkpoint(checkpoint)

    assert logged == [str(checkpoint)]


def test_log_training_result_records_history_best_metrics_and_checkpoint(
    monkeypatch,
    tmp_path,
):
    checkpoint = tmp_path / "model.pt"
    result = SimpleNamespace(
        history=[{"epoch": 1, "accuracy": 0.75}],
        best_metrics={"accuracy": 0.75},
        best_epoch=1,
    )
    calls = []

    monkeypatch.setattr(
        mlflow_setup,
        "log_history",
        lambda history: calls.append(("history", history)),
    )
    monkeypatch.setattr(
        mlflow_setup,
        "log_best",
        lambda metrics, epoch: calls.append(("best", metrics, epoch)),
    )
    monkeypatch.setattr(
        mlflow_setup,
        "log_checkpoint",
        lambda path: calls.append(("checkpoint", path)),
    )

    mlflow_setup.log_training_result(result, checkpoint)

    assert calls == [
        ("history", result.history),
        ("best", result.best_metrics, result.best_epoch),
        ("checkpoint", checkpoint),
    ]


def test_log_optimization_trial_records_parameters_metrics_and_state(monkeypatch):
    calls = []
    monkeypatch.setattr(
        mlflow_setup.mlflow,
        "log_params",
        lambda params: calls.append(("params", params)),
    )
    monkeypatch.setattr(
        mlflow_setup.mlflow,
        "set_tag",
        lambda key, value: calls.append(("tag", key, value)),
    )
    monkeypatch.setattr(
        mlflow_setup.mlflow,
        "log_metric",
        lambda key, value: calls.append(("metric", key, value)),
    )
    trial = SimpleNamespace(
        params={"dropout": 0.2, "batch_size": 16},
        user_attrs={
            "fold_metrics": [
                {
                    "fold": 0,
                    "roc_auc": 0.8,
                    "accuracy": 0.75,
                    "f1": 0.7,
                    "train_loss": 0.4,
                    "validation_loss": 0.5,
                    "duration_seconds": 2.5,
                }
            ],
            "mean_roc_auc": 0.8,
            "mean_accuracy": 0.75,
            "mean_f1": 0.7,
            "runtime_seconds": 2.5,
        },
    )

    mlflow_setup.log_optimization_trial(trial, 0.8, "complete")

    assert calls[:3] == [
        ("params", trial.params),
        ("tag", "optuna_state", "complete"),
        ("metric", "objective_mean_roc_auc", 0.8),
    ]
    assert ("metric", "fold_0_roc_auc", 0.8) in calls
    assert ("metric", "mean_f1", 0.7) in calls
    assert ("metric", "runtime_seconds", 2.5) in calls
