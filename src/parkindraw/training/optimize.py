"""Optuna objective for classification-head hyperparameter search."""

from collections.abc import Callable
from dataclasses import replace
from time import perf_counter

import numpy as np
import optuna

from parkindraw.training.config import TrainingConfig
from parkindraw.training.optimization_config import OptimizationConfig
from parkindraw.training.trainer import TrainingResult, train_fold


class OptimizationError(RuntimeError):
    """Raised when a trial cannot produce the required validation objective."""


TrainFold = Callable[[TrainingConfig], TrainingResult]


def suggest_hyperparameters(
    trial: optuna.Trial,
    config: OptimizationConfig,
) -> dict:
    """Suggest exactly the bounded search space approved for Phase 3."""
    return {
        "learning_rate": trial.suggest_float(
            "learning_rate",
            config.learning_rate_low,
            config.learning_rate_high,
            log=True,
        ),
        "weight_decay": trial.suggest_float(
            "weight_decay",
            config.weight_decay_low,
            config.weight_decay_high,
            log=True,
        ),
        "dropout": trial.suggest_float(
            "dropout",
            config.dropout_low,
            config.dropout_high,
            step=config.dropout_step,
        ),
        "batch_size": trial.suggest_categorical(
            "batch_size",
            list(config.batch_sizes),
        ),
    }


def build_trial_config(
    base: TrainingConfig,
    drawing_type: str,
    fold: int,
    parameters: dict,
) -> TrainingConfig:
    """Apply one trial's parameters without mutating the base configuration."""
    return replace(
        base,
        drawing_type=drawing_type,
        fold=fold,
        **parameters,
    )


def _fold_record(fold: int, result: TrainingResult, duration: float) -> dict:
    metrics = result.best_metrics
    roc_auc = metrics.get("roc_auc")
    if roc_auc is None:
        raise OptimizationError(
            f"fold {fold} produced no ROC-AUC; validation must contain both classes"
        )

    history = result.history[result.best_epoch - 1]
    return {
        "fold": fold,
        "best_epoch": result.best_epoch,
        "roc_auc": float(roc_auc),
        "accuracy": float(metrics["accuracy"]),
        "f1": float(metrics["f1"]),
        "train_loss": float(history["train_loss"]),
        "validation_loss": float(history["validation_loss"]),
        "duration_seconds": round(duration, 4),
        "history": result.history,
    }


def _record_trial_summary(
    trial: optuna.Trial,
    fold_metrics: list[dict],
    started_at: float,
) -> None:
    """Persist secondary metrics as JSON-safe Optuna trial attributes."""
    trial.set_user_attr("fold_metrics", fold_metrics)
    if fold_metrics:
        trial.set_user_attr(
            "mean_roc_auc",
            float(np.mean([entry["roc_auc"] for entry in fold_metrics])),
        )
        trial.set_user_attr(
            "mean_accuracy",
            float(np.mean([entry["accuracy"] for entry in fold_metrics])),
        )
        trial.set_user_attr(
            "mean_f1",
            float(np.mean([entry["f1"] for entry in fold_metrics])),
        )
    trial.set_user_attr("runtime_seconds", round(perf_counter() - started_at, 4))


def evaluate_trial(
    trial: optuna.Trial,
    base_config: TrainingConfig,
    optimization_config: OptimizationConfig,
    drawing_type: str,
    *,
    train: TrainFold | None = None,
) -> float:
    """Evaluate one parameter set across development folds only."""
    train = train or train_fold
    parameters = suggest_hyperparameters(trial, optimization_config)
    trial.set_user_attr("drawing_type", drawing_type)
    fold_metrics = []
    started_at = perf_counter()

    for fold in range(optimization_config.n_splits):
        fold_config = build_trial_config(
            base_config,
            drawing_type,
            fold,
            parameters,
        )
        fold_started_at = perf_counter()
        result = train(fold_config)
        fold_metrics.append(
            _fold_record(fold, result, perf_counter() - fold_started_at)
        )

        running_mean = float(
            np.mean([entry["roc_auc"] for entry in fold_metrics])
        )
        _record_trial_summary(trial, fold_metrics, started_at)
        trial.report(running_mean, step=fold)
        if trial.should_prune():
            raise optuna.TrialPruned(
                f"pruned after fold {fold} with mean ROC-AUC {running_mean:.4f}"
            )

    return float(np.mean([entry["roc_auc"] for entry in fold_metrics]))
