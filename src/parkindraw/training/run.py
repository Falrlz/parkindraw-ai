"""CLI entry point: train one fold from a config file.

The config is the unit of reproducibility. Any setting may be overridden on the
command line for a quick smoke run, but the override is recorded in MLflow
alongside everything else, so a run can always be reconstructed.
"""

import argparse
import json

from parkindraw.pipelines.training import run_training_pipeline
from parkindraw.tracking import mlflow_setup
from parkindraw.training.config import load_training_config

DEFAULT_CONFIG = "configs/experiments/resnet18.yaml"
DEFAULT_CHECKPOINT_DIR = "artifacts/checkpoints"

# Temporary compatibility alias for callers of the original CLI module.
load_config = load_training_config


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train one frozen ResNet-18 fold from a config file.",
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--drawing-type", choices=("circle", "meander", "spiral"))
    parser.add_argument("--fold", type=int)
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--batch-size", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--device")
    parser.add_argument("--checkpoint-dir", default=DEFAULT_CHECKPOINT_DIR)
    parser.add_argument(
        "--no-tracking",
        action="store_true",
        help="Skip MLflow, for a quick local check.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    config = load_training_config(
        args.config,
        drawing_type=args.drawing_type,
        fold=args.fold,
        epochs=args.epochs,
        batch_size=args.batch_size,
        seed=args.seed,
        device=args.device,
    )

    pipeline_result = run_training_pipeline(
        config,
        args.checkpoint_dir,
        tracker=None if args.no_tracking else mlflow_setup,
    )
    result = pipeline_result.training

    print(f"Run: {pipeline_result.run_name}")
    print(f"Best epoch: {result.best_epoch} of {len(result.history)} run")
    print(json.dumps(result.best_metrics, indent=2))
    print(f"Checkpoint: {pipeline_result.checkpoint_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
