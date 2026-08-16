"""Reusable orchestration for one training run."""

import logging
from contextlib import AbstractContextManager, nullcontext
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol

from parkindraw.training.config import TrainingConfig
from parkindraw.training.trainer import TrainingResult, train_fold

logger = logging.getLogger(__name__)


class TrainingTracker(Protocol):
    """Tracking operations required by the training pipeline."""

    def configure(self) -> None: ...

    def start_run(
        self,
        name: str,
        config: dict,
    ) -> AbstractContextManager[object]: ...

    def log_training_result(
        self,
        result: TrainingResult,
        checkpoint_path: str | Path,
    ) -> None: ...


@dataclass(frozen=True)
class TrainingPipelineResult:
    """Training output together with the identity and artifact of its run."""

    run_name: str
    checkpoint_path: Path
    training: TrainingResult


def build_run_name(config: TrainingConfig) -> str:
    """Build a stable identity from the drawing type and validation fold."""
    return f"{config.drawing_type}-fold{config.fold}"


def run_training_pipeline(
    config: TrainingConfig,
    checkpoint_dir: str | Path,
    *,
    tracker: TrainingTracker | None = None,
) -> TrainingPipelineResult:
    """Train one fold and optionally record the completed run."""
    name = build_run_name(config)
    checkpoint_path = Path(checkpoint_dir) / f"{name}.pt"

    logger.info(
        "Starting training pipeline for %s drawings on fold %d",
        config.drawing_type,
        config.fold,
    )

    run_context: AbstractContextManager[object] = nullcontext()
    if tracker is not None:
        tracker.configure()
        run_context = tracker.start_run(name, asdict(config))

    with run_context:
        training = train_fold(config, checkpoint_path)
        if tracker is not None:
            tracker.log_training_result(training, checkpoint_path)

    logger.info(
        "Completed training pipeline at epoch %d with metrics %s; checkpoint=%s",
        training.best_epoch,
        training.best_metrics,
        checkpoint_path,
    )
    return TrainingPipelineResult(
        run_name=name,
        checkpoint_path=checkpoint_path,
        training=training,
    )
