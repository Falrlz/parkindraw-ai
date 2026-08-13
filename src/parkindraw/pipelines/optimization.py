"""Persistent Optuna-study orchestration for development-fold tuning."""

from __future__ import annotations

import json
import logging
from contextlib import AbstractContextManager, nullcontext
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

import optuna

from parkindraw.training.config import TrainingConfig, load_training_config
from parkindraw.training.optimization_config import OptimizationConfig
from parkindraw.training.optimize import evaluate_trial

logger = logging.getLogger(__name__)


class OptimizationError(RuntimeError):
    """Raised when a study finishes without a usable completed trial."""


class OptimizationTracker(Protocol):
    """Tracking operations required by the optimization pipeline."""

    def configure(self) -> None: ...

    def start_run(
        self,
        name: str,
        config: dict,
    ) -> AbstractContextManager[object]: ...

    def log_optimization_trial(
        self,
        trial: optuna.Trial,
        value: float | None,
        state: str,
    ) -> None: ...


@dataclass(frozen=True)
class OptimizationStudyResult:
    """Serializable identity and winning result for one drawing study."""

    drawing_type: str
    study_name: str
    storage: str | None
    trial_count: int
    best_trial_number: int
    best_value: float
    best_params: dict
    summary_path: Path


@dataclass(frozen=True)
class OptimizationPipelineResult:
    """Results from all requested drawing-specific studies."""

    studies: tuple[OptimizationStudyResult, ...]


def build_study_name(drawing_type: str) -> str:
    """Return a stable name so an interrupted study can be resumed."""
    return f"parkindraw-{drawing_type}-head"


def _storage_url(study_db: str | None) -> tuple[str | None, str | None]:
    if study_db is None:
        return None, None
    path = Path(study_db).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path.as_posix()}", str(path)


def _run_id(active_run: object | None) -> str | None:
    info = getattr(active_run, "info", None)
    value = getattr(info, "run_id", None)
    return str(value) if value is not None else None


def _tracking_config(
    base_config: TrainingConfig,
    drawing_type: str,
    study_name: str,
    trial_number: int,
) -> dict:
    values = {
        f"base_{key}": value
        for key, value in asdict(base_config).items()
        if value is not None
    }
    values.update(
        {
            "study_name": study_name,
            "drawing_type": drawing_type,
            "trial_number": trial_number,
        }
    )
    return values


def _study_definition(
    base_config: TrainingConfig,
    config: OptimizationConfig,
    drawing_type: str,
) -> dict:
    """Describe every setting that must remain fixed across resumed trials."""
    return {
        "schema_version": 1,
        "drawing_type": drawing_type,
        "base_training_config": asdict(base_config),
        "n_splits": config.n_splits,
        "study_seed": config.study_seed,
        "search_space": {
            "learning_rate": [
                config.learning_rate_low,
                config.learning_rate_high,
                "log",
            ],
            "weight_decay": [
                config.weight_decay_low,
                config.weight_decay_high,
                "log",
            ],
            "dropout": [
                config.dropout_low,
                config.dropout_high,
                config.dropout_step,
            ],
            "batch_size": list(config.batch_sizes),
        },
        "pruner": {
            "name": "MedianPruner",
            "startup_trials": config.pruner_startup_trials,
            "warmup_steps": config.pruner_warmup_steps,
        },
    }


def _validate_study_contract(
    study: optuna.Study,
    definition: dict,
    total_budget: int,
) -> None:
    existing = study.user_attrs.get("definition")
    if existing is None:
        if study.trials:
            raise OptimizationError(
                f"study {study.study_name!r} has trials but no definition metadata"
            )
        study.set_user_attr("definition", definition)
    elif existing != definition:
        raise OptimizationError(
            f"study {study.study_name!r} definition does not match this config; "
            "use the original config or a separate study database"
        )

    if len(study.trials) > total_budget:
        raise OptimizationError(
            f"study {study.study_name!r} already has {len(study.trials)} trials, "
            f"which exceeds the requested total budget of {total_budget}"
        )


def _objective(
    trial: optuna.Trial,
    *,
    base_config: TrainingConfig,
    optimization_config: OptimizationConfig,
    drawing_type: str,
    study_name: str,
    tracker: OptimizationTracker | None,
) -> float:
    run_context: AbstractContextManager[object] = nullcontext()
    if tracker is not None:
        run_context = tracker.start_run(
            f"{study_name}-trial{trial.number}",
            _tracking_config(
                base_config,
                drawing_type,
                study_name,
                trial.number,
            ),
        )

    with run_context as active_run:
        try:
            value = evaluate_trial(
                trial,
                base_config,
                optimization_config,
                drawing_type,
            )
        except optuna.TrialPruned:
            run_id = _run_id(active_run)
            if run_id is not None:
                trial.set_user_attr("mlflow_run_id", run_id)
            if tracker is not None:
                tracker.log_optimization_trial(trial, None, "pruned")
            raise
        except Exception:
            run_id = _run_id(active_run)
            if run_id is not None:
                trial.set_user_attr("mlflow_run_id", run_id)
            if tracker is not None:
                tracker.log_optimization_trial(trial, None, "failed")
            raise

        run_id = _run_id(active_run)
        if run_id is not None:
            trial.set_user_attr("mlflow_run_id", run_id)
        if tracker is not None:
            tracker.log_optimization_trial(trial, value, "complete")
        return value


def _serialize_trial(trial: optuna.trial.FrozenTrial) -> dict:
    duration = trial.duration.total_seconds() if trial.duration is not None else None
    return {
        "number": trial.number,
        "state": trial.state.name.lower(),
        "value": trial.value,
        "params": trial.params,
        "user_attrs": trial.user_attrs,
        "started_at": _isoformat(trial.datetime_start),
        "completed_at": _isoformat(trial.datetime_complete),
        "duration_seconds": duration,
    }


def _isoformat(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _write_summary(
    *,
    study: optuna.Study,
    drawing_type: str,
    storage_path: str | None,
    base_config: TrainingConfig,
    optimization_config: OptimizationConfig,
) -> Path:
    try:
        best = study.best_trial
    except ValueError as error:
        raise OptimizationError(
            f"study {study.study_name!r} has no completed trials"
        ) from error

    output_dir = Path(optimization_config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{drawing_type}.json"
    payload = {
        "drawing_type": drawing_type,
        "study_name": study.study_name,
        "storage": storage_path,
        "objective": "mean_validation_subject_roc_auc",
        "direction": study.direction.name.lower(),
        "base_training_config": asdict(base_config),
        "optimization_config": asdict(optimization_config),
        "best_trial": _serialize_trial(best),
        "trials": [_serialize_trial(trial) for trial in study.trials],
    }
    temporary_path = output_path.with_suffix(".json.tmp")
    temporary_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    temporary_path.replace(output_path)
    return output_path


def run_optimization_pipeline(
    config: OptimizationConfig,
    *,
    training_overrides: dict | None = None,
    tracker: OptimizationTracker | None = None,
) -> OptimizationPipelineResult:
    """Run or resume one bounded study per requested drawing type."""
    base_config = load_training_config(
        config.training_config,
        **(training_overrides or {}),
    )
    storage_url, storage_path = _storage_url(config.study_db)
    if tracker is not None:
        tracker.configure()

    results = []
    for drawing_type in config.drawing_types:
        study_name = build_study_name(drawing_type)
        study = optuna.create_study(
            study_name=study_name,
            storage=storage_url,
            direction="maximize",
            sampler=optuna.samplers.TPESampler(seed=config.study_seed),
            pruner=optuna.pruners.MedianPruner(
                n_startup_trials=config.pruner_startup_trials,
                n_warmup_steps=config.pruner_warmup_steps,
            ),
            load_if_exists=True,
        )
        _validate_study_contract(
            study,
            _study_definition(base_config, config, drawing_type),
            config.n_trials,
        )
        study.set_user_attr("drawing_type", drawing_type)
        study.set_user_attr("objective", "mean_validation_subject_roc_auc")

        remaining_trials = max(0, config.n_trials - len(study.trials))
        if remaining_trials:
            logger.info(
                "Running %d remaining trial(s) for %s",
                remaining_trials,
                drawing_type,
            )
            study.optimize(
                lambda trial: _objective(
                    trial,
                    base_config=base_config,
                    optimization_config=config,
                    drawing_type=drawing_type,
                    study_name=study_name,
                    tracker=tracker,
                ),
                n_trials=remaining_trials,
                timeout=config.timeout_seconds,
            )
        else:
            logger.info(
                "Study %s already reached its %d-trial budget",
                study_name,
                config.n_trials,
            )

        summary_path = _write_summary(
            study=study,
            drawing_type=drawing_type,
            storage_path=storage_path,
            base_config=base_config,
            optimization_config=config,
        )
        best = study.best_trial
        results.append(
            OptimizationStudyResult(
                drawing_type=drawing_type,
                study_name=study_name,
                storage=storage_path,
                trial_count=len(study.trials),
                best_trial_number=best.number,
                best_value=float(best.value),
                best_params=best.params,
                summary_path=summary_path,
            )
        )

    return OptimizationPipelineResult(studies=tuple(results))
