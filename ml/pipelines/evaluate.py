"""Locked holdout evaluation pipeline orchestrator."""

import argparse
from pathlib import Path
from typing import Any

from src.config.config import (
    DEFAULT_CONFIG_PATH,
    DRAWING_TYPES,
    SPLITS_DIR,
    load_config,
)
from src.data.manifest import filter_holdout, load_manifest
from src.evaluation.evaluator import (
    evaluate_holdout_models,
    generate_evaluation_reports,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_evaluation_pipeline(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    drawing_types: list[str] | tuple[str, ...] | None = None,
    ) -> dict[str, dict[str, Any]]:

    """Execute the locked holdout evaluation pipeline."""
    logger.info("=== Starting Model Evaluation Pipeline (Locked Holdout) ===")

    # Step 1: Load experiment configuration
    logger.info("Step 1: Loading experiment configuration from '%s'...", config_path)
    cfg = load_config(config_path)

    # Step 2: Load locked holdout dataset partition
    splits_dir = cfg.get("splits_dir", SPLITS_DIR)
    logger.info("Step 2: Loading locked holdout test partition from '%s'...", splits_dir)
    manifest = load_manifest(splits_dir)
    holdout_df = filter_holdout(manifest)

    # Step 3: Run holdout evaluation service
    target_drawings = drawing_types or cfg.get("drawing_types", DRAWING_TYPES)
    logger.info("Step 3: Evaluating models on holdout test set for: %s...", target_drawings)
    results = evaluate_holdout_models(holdout_df, cfg, drawing_types=target_drawings)

    # Step 4: Generate evaluation figures and reports
    logger.info("Step 4: Generating confusion matrices and learning curves...")
    generate_evaluation_reports(results, cfg)

    logger.info("=== Model Evaluation Completed Successfully ===")
    return results


def main(
    argv: list[str] | None = None,
    ) -> int:

    """CLI entry point for holdout evaluation pipeline."""
    parser = argparse.ArgumentParser(description="Locked holdout evaluation pipeline orchestrator.")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to YAML configuration.")
    parser.add_argument(
        "--drawing-type",
        choices=["all", "circle", "meander", "spiral"],
        default="all",
        help="Target drawing modality ('all' for all).",
    )
    args = parser.parse_args(argv)

    drawings = None if args.drawing_type == "all" else [args.drawing_type]
    run_evaluation_pipeline(config_path=args.config, drawing_types=drawings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
