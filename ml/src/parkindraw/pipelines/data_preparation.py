"""Reusable orchestration for the dataset preparation pipeline."""

import logging
from dataclasses import dataclass
from pathlib import Path

from parkindraw.data.splits import (
    DEFAULT_HOLDOUT_SIZE,
    DEFAULT_N_SPLITS,
    DEFAULT_SEED,
    run_split,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DataPreparationResult:
    """Structured result of one data preparation run."""

    summary: dict
    output_dir: Path
    master_manifest_path: Path
    sessions_path: Path
    split_config_path: Path


def run_data_preparation_pipeline(
    raw_dir: str | Path = "data/raw",
    output_dir: str | Path = "data/splits",
    *,
    holdout_size: float = DEFAULT_HOLDOUT_SIZE,
    n_splits: int = DEFAULT_N_SPLITS,
    seed: int = DEFAULT_SEED,
) -> DataPreparationResult:
    """Execute the end-to-end data preparation workflow.

    1. Parse and validate raw image filenames and folder schema.
    2. Hash images and cluster duplicate subjects.
    3. Generate holdout set (20%) and StratifiedGroupKFold splits (80%).
    4. Audit data for zero subject/hash leakage.
    5. Write `master_manifest.csv`, `sessions.csv`, and `split_config.json`.
    """
    out = Path(output_dir)
    logger.info("Starting data preparation pipeline from %s to %s", raw_dir, output_dir)

    summary = run_split(
        raw_dir=raw_dir,
        output_dir=output_dir,
        holdout_size=holdout_size,
        n_splits=n_splits,
        seed=seed,
    )

    logger.info(
        "Data preparation complete: %d subjects (%d dev, %d holdout), %d duplicate clusters merged",
        summary["total_subjects"],
        summary["development_subjects"],
        summary["holdout_subjects"],
        len(summary["duplicate_clusters"]),
    )

    return DataPreparationResult(
        summary=summary,
        output_dir=out,
        master_manifest_path=out / "master_manifest.csv",
        sessions_path=out / "sessions.csv",
        split_config_path=out / "split_config.json",
    )
