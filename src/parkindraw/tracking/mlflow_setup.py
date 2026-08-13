"""Local MLflow tracking.

Every run records the config it came from, its per-epoch history, and the
resulting checkpoint. Without that, a good number cannot be traced back to the
settings that produced it, and Phase 3 comparisons become guesswork.

A local SQLite file backs the tracking store. The older filesystem store is in
maintenance mode as of MLflow 3.14 and refuses to start, and SQLite is also
what the Phase 5 tracking server will use, so the backend does not change
underneath us later.

Both the database and the artifacts are regenerable runtime state, not source,
and are ignored by Git.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

import mlflow

if TYPE_CHECKING:
    import optuna

    from parkindraw.training.trainer import TrainingResult

DEFAULT_TRACKING_DB = "mlflow.db"
DEFAULT_ARTIFACT_DIR = "mlruns"
DEFAULT_EXPERIMENT = "parkindraw"

logger = logging.getLogger(__name__)


def configure(
    tracking_db: str | Path = DEFAULT_TRACKING_DB,
    artifact_dir: str | Path = DEFAULT_ARTIFACT_DIR,
    experiment: str = DEFAULT_EXPERIMENT,
) -> None:
    """Point MLflow at a local SQLite store and select the experiment."""
    database = Path(tracking_db).resolve()
    artifacts = Path(artifact_dir).resolve()
    artifacts.mkdir(parents=True, exist_ok=True)

    mlflow.set_tracking_uri(f"sqlite:///{database.as_posix()}")
    if mlflow.get_experiment_by_name(experiment) is None:
        mlflow.create_experiment(experiment, artifact_location=artifacts.as_uri())
    mlflow.set_experiment(experiment)
    logger.info("Configured MLflow experiment %s", experiment)


@contextmanager
def start_run(name: str, config: dict):
    """Open a run with its parameters already logged."""
    logger.info("Starting MLflow run %s", name)
    with mlflow.start_run(run_name=name) as active:
        mlflow.log_params(config)
        yield active


def log_history(history: list[dict]) -> None:
    """Log every numeric metric per epoch, so learning curves are inspectable."""
    for entry in history:
        step = entry["epoch"]
        for key, value in entry.items():
            if key != "epoch" and isinstance(value, (int, float)):
                mlflow.log_metric(key, value, step=step)


def log_best(metrics: dict, best_epoch: int) -> None:
    """Log the selected epoch's metrics under a `best_` prefix."""
    mlflow.log_metric("best_epoch", best_epoch)
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            mlflow.log_metric(f"best_{key}", value)


def log_checkpoint(checkpoint_path: str | Path) -> None:
    if Path(checkpoint_path).is_file():
        mlflow.log_artifact(str(checkpoint_path))


def log_training_result(
    result: TrainingResult,
    checkpoint_path: str | Path,
) -> None:
    """Record a completed training result and its checkpoint artifact."""
    log_history(result.history)
    log_best(result.best_metrics, result.best_epoch)
    log_checkpoint(checkpoint_path)
    logger.info(
        "Logged training result from epoch %d and checkpoint %s",
        result.best_epoch,
        checkpoint_path,
    )


def log_optimization_trial(
    trial: optuna.Trial,
    value: float | None,
    state: str,
) -> None:
    """Record one Optuna trial's parameters, fold metrics, and outcome."""
    mlflow.log_params(trial.params)
    mlflow.set_tag("optuna_state", state)
    if value is not None:
        mlflow.log_metric("objective_mean_roc_auc", value)

    for entry in trial.user_attrs.get("fold_metrics", []):
        fold = int(entry["fold"])
        for key in (
            "roc_auc",
            "accuracy",
            "f1",
            "train_loss",
            "validation_loss",
            "duration_seconds",
        ):
            metric = entry.get(key)
            if isinstance(metric, (int, float)):
                mlflow.log_metric(f"fold_{fold}_{key}", metric)

    for key in ("mean_roc_auc", "mean_accuracy", "mean_f1", "runtime_seconds"):
        metric = trial.user_attrs.get(key)
        if isinstance(metric, (int, float)):
            mlflow.log_metric(key, metric)
