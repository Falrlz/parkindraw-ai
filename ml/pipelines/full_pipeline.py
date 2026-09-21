"""Master orchestrator pipeline for ParkinDraw AI."""

import argparse
from pathlib import Path
from typing import Any

from pipelines.evaluate import run_evaluation_pipeline
from pipelines.preparation import run_preparation_pipeline
from pipelines.train import run_training_pipeline
from src.config.config import TRAIN_CONFIG_PATH
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_full_pipeline(
    train_config_path: str | Path = TRAIN_CONFIG_PATH,
    drawing_types: list[str] | tuple[str, ...] | None = None,
    overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

    """Execute the complete end-to-end ML pipeline."""
    logger.info("==================================================")
    logger.info("   Starting Full End-to-End ParkinDraw Pipeline   ")
    logger.info("==================================================")

    # Stage 1: Data Preparation
    logger.info(">>> STAGE 1 / 3: DATA PREPARATION <<<")
    run_preparation_pipeline()

    # Stage 2: Model Training
    logger.info(">>> STAGE 2 / 3: MULTI-DRAWING TRAINING <<<")
    train_results = run_training_pipeline(
        config_path=train_config_path,
        drawing_types=drawing_types,
        overrides=overrides,
    )

    # Stage 3: Holdout Evaluation
    logger.info(">>> STAGE 3 / 3: LOCKED HOLDOUT EVALUATION <<<")
    eval_results = run_evaluation_pipeline(
        config_path=train_config_path,
        drawing_types=drawing_types,
    )

    logger.info("==================================================")
    logger.info("   Full Pipeline Finished Successfully!           ")
    logger.info("==================================================")

    return {
        "training": train_results,
        "evaluation": eval_results,
    }


def main(
    argv: list[str] | None = None,
    ) -> int:

    """CLI entry point for master pipeline."""
    parser = argparse.ArgumentParser(description="Master end-to-end ParkinDraw ML pipeline.")
    parser.add_argument("--config", default=TRAIN_CONFIG_PATH, help="Path to training YAML configuration.")
    parser.add_argument(
        "--drawing-type",
        choices=["all", "circle", "meander", "spiral"],
        default="all",
        help="Target drawing modality ('all' for all).",
    )
    parser.add_argument("--epochs", type=int, default=None, help="Override number of epochs.")
    parser.add_argument("--batch-size", type=int, default=None, help="Override batch size.")
    parser.add_argument("--lr", type=float, default=None, help="Override learning rate.")
    parser.add_argument(
        "--fold",
        default=None,
        help="Override fold index ('0', '1', '2') or 'all' for full cross-validation.",
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

    run_full_pipeline(
        train_config_path=args.config,
        drawing_types=drawings,
        overrides=overrides,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
