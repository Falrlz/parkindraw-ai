"""Multi-drawing model training pipeline orchestrator."""

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from pipelines.preparation import run_preparation_pipeline
from src.config.config import (
    DEFAULT_CONFIG_PATH,
    DRAWING_TYPES,
    RAW_DATA_DIR,
    SPLITS_DIR,
    load_config,
)
from src.data.manifest import load_manifest
from src.training.trainer import train_drawing_models
from src.utils.logger import get_logger

logger = get_logger(__name__)

ALL_DRAWING_TYPES: tuple[str, ...] = DRAWING_TYPES


def load_or_create_manifest(
    cfg: dict[str, Any],
    ) -> pd.DataFrame:

    """Load master_manifest.csv or trigger preparation pipeline if missing."""
    splits_dir = Path(cfg.get("splits_dir", SPLITS_DIR))
    manifest_path = splits_dir / "master_manifest.csv"

    if not manifest_path.is_file():
        logger.info("Manifest missing. Triggering data preparation pipeline...")
        run_preparation_pipeline(
            raw_dir=cfg.get("raw_dir", RAW_DATA_DIR),
            output_dir=splits_dir,
            seed=int(cfg.get("seed", 42)),
        )

    return load_manifest(splits_dir)


def run_training_pipeline(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    drawing_types: list[str] | tuple[str, ...] | None = None,
    overrides: dict[str, Any] | None = None,
    ) -> dict[str, dict[str, Any]]:

    """Execute the multi-drawing training pipeline across target modalities."""
    logger.info("=== Starting Model Training Pipeline ===")

    # Step 1: Load experiment configuration & merge overrides
    logger.info("Step 1: Loading experiment configuration from '%s'...", config_path)
    cfg = load_config(config_path)
    config = dict(cfg)
    if overrides:
        config.update({k: v for k, v in overrides.items() if v is not None})

    # Step 2: Load master dataset manifest
    logger.info("Step 2: Loading master dataset manifest...")
    master_manifest = load_or_create_manifest(config)

    # Step 3: Run training orchestration across modalities and folds
    target_drawings = drawing_types or config.get("drawing_types", DRAWING_TYPES)
    logger.info("Step 3: Training ResNet-18 models for modalities: %s...", target_drawings)
    results = train_drawing_models(
        master_manifest=master_manifest,
        cfg=config,
        drawing_types=target_drawings,
    )

    logger.info("=== Model Training Completed Successfully ===")
    return results


def main(
    argv: list[str] | None = None,
    ) -> int:

    """CLI entry point for training pipeline."""
    parser = argparse.ArgumentParser(description="Multi-drawing training pipeline orchestrator.")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to YAML configuration.")
    parser.add_argument(
        "--drawing-type",
        choices=["all", "circle", "meander", "spiral"],
        default="all",
        help="Target drawing modality ('all' for circle, meander, and spiral).",
    )
    parser.add_argument("--epochs", type=int, default=None, help="Override number of epochs.")
    parser.add_argument("--batch-size", type=int, default=None, help="Override batch size.")
    parser.add_argument("--lr", type=float, default=None, help="Override learning rate.")
    parser.add_argument(
        "--fold",
        default=None,
        help="Override fold index ('0', '1', '2') or 'all' for full 3-fold cross-validation.",
    )
    parser.add_argument("--device", default=None, help="Override device ('cpu', 'cuda', 'auto').")
    args = parser.parse_args(argv)

    drawings = None if args.drawing_type == "all" else [args.drawing_type]
    fold_override: str | int | None = None
    if args.fold is not None:
        fold_override = "all" if str(args.fold).strip().lower() == "all" else int(args.fold)

    overrides = {
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.lr,
        "fold": fold_override,
        "device": args.device,
    }

    run_training_pipeline(config_path=args.config, drawing_types=drawings, overrides=overrides)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
