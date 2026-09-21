import json
import logging
from pathlib import Path
from typing import Any

import mlflow

from src.config.config import (
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_TRACKING_URI,
    MODELS_DIR,
)
from src.models.resnet18 import FrozenResNet18, save_head

logger = logging.getLogger(__name__)

DEFAULT_EXPERIMENT = MLFLOW_EXPERIMENT_NAME


def silence_mlflow_loggers(
    ) -> None:

    """Silence internal MLflow loggers to keep console output clean."""
    for name in logging.root.manager.loggerDict:
        if name.startswith("mlflow"):
            logging.getLogger(name).setLevel(logging.ERROR)


def setup_mlflow(
    tracking_uri: str | None = MLFLOW_TRACKING_URI,
    experiment_name: str = DEFAULT_EXPERIMENT,
    ) -> None:

    """Configure MLflow tracking URI and active experiment."""
    silence_mlflow_loggers()
    if tracking_uri:
        if tracking_uri.startswith("sqlite:///"):
            db_path = Path(tracking_uri.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(tracking_uri)
        logger.info("MLflow URI: %s", tracking_uri)
    mlflow.set_experiment(experiment_name)
    logger.info("MLflow Experiment: %s", experiment_name)


def serialize_params(
    params: dict[str, Any],
    ) -> dict[str, str | int | float | bool]:

    """Sanitize configuration parameters into scalar types for MLflow."""
    clean: dict[str, str | int | float | bool] = {}
    for k, v in params.items():
        if isinstance(v, (int, float, str, bool)):
            clean[k] = v
        elif isinstance(v, Path):
            clean[k] = str(v)
        elif isinstance(v, (dict, list)):
            clean[k] = json.dumps(v)
        else:
            clean[k] = str(v)
    return clean


def log_training_run(
    run_name: str,
    drawing_type: str,
    model: FrozenResNet18,
    params: dict[str, Any],
    metrics: dict[str, float],
    duration: float,
    *,
    history: dict[str, list[float]] | None = None,
    checkpoint_dir: str | Path = MODELS_DIR,
    model_filename: str | None = None,
    phase: str = "baseline",
    extra_tags: dict[str, str] | None = None,
    ) -> Path:

    """Log training run parameters, metrics, history, and model artifact to MLflow."""
    silence_mlflow_loggers()

    # 1. Save classification head weights locally
    out_dir = Path(checkpoint_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target_filename = model_filename or f"resnet18_{drawing_type}.pt"
    model_path = out_dir / target_filename
    save_head(model, model_path)

    # 2. Record to MLflow
    tags = {"drawing_type": drawing_type, "model_type": "FrozenResNet18", "phase": phase}
    if extra_tags:
        tags.update(extra_tags)

    with mlflow.start_run(run_name=run_name):
        mlflow.set_tags(tags)
        mlflow.log_params({**serialize_params(params), "drawing_type": drawing_type})

        if history:
            num_epochs = len(history.get("train_loss", []))
            for ep in range(num_epochs):
                for k, vals in history.items():
                    if ep < len(vals):
                        mlflow.log_metric(f"epoch_{k}", vals[ep], step=ep + 1)

        for k, v in metrics.items():
            mlflow.log_metric(k, v)
        mlflow.log_metric("train_duration_seconds", duration)
        mlflow.log_artifact(str(model_path), artifact_path="weights")

    logger.info("Successfully logged run '%s' to MLflow (model: %s).", run_name, model_path)
    return model_path
