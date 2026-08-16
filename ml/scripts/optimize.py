"""Command-line entry point for bounded ParkinDraw Optuna studies."""

import argparse
import json

from parkindraw.pipelines.optimization import run_optimization_pipeline
from parkindraw.tracking import mlflow_setup
from parkindraw.training.optimization_config import load_optimization_config

DEFAULT_CONFIG = "configs/experiments/optuna.yaml"


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the supported optimization CLI without parsing it."""
    parser = argparse.ArgumentParser(
        prog="parkindraw-optimize",
        description="Run or resume bounded Optuna studies on development folds.",
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument(
        "--drawing-type",
        choices=("circle", "meander", "spiral"),
        help="Run only one drawing-specific study.",
    )
    parser.add_argument("--n-trials", type=int)
    parser.add_argument("--timeout-seconds", type=float)
    parser.add_argument("--study-db")
    parser.add_argument("--output-dir")
    parser.add_argument(
        "--epochs",
        type=int,
        help="Override training epochs, primarily for a smoke run.",
    )
    parser.add_argument("--device")
    parser.add_argument(
        "--no-tracking",
        action="store_true",
        help="Skip MLflow while retaining Optuna persistence and summaries.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Translate CLI arguments into the reusable optimization pipeline."""
    args = build_argument_parser().parse_args(argv)
    config = load_optimization_config(
        args.config,
        drawing_types=(args.drawing_type,) if args.drawing_type else None,
        n_trials=args.n_trials,
        timeout_seconds=args.timeout_seconds,
        study_db=args.study_db,
        output_dir=args.output_dir,
    )
    training_overrides = {
        key: value
        for key, value in {"epochs": args.epochs, "device": args.device}.items()
        if value is not None
    }
    result = run_optimization_pipeline(
        config,
        training_overrides=training_overrides,
        tracker=None if args.no_tracking else mlflow_setup,
    )

    for study in result.studies:
        print(f"Study: {study.study_name} ({study.trial_count} trials)")
        print(f"Best validation ROC-AUC: {study.best_value:.6f}")
        print(json.dumps(study.best_params, indent=2, sort_keys=True))
        print(f"Summary: {study.summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
