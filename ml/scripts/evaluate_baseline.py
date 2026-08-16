"""Command-line entry point for metadata-only baseline evaluation."""

import argparse

from parkindraw.evaluation.baseline import (
    DEFAULT_N_SPLITS,
    DEFAULT_SEED,
    FEATURES,
    run_baseline,
)


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the supported metadata-baseline command-line interface."""
    parser = argparse.ArgumentParser(
        prog="parkindraw-evaluate-baseline",
        description="Measure the metadata-only baseline that any model must beat.",
    )
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--splits-dir", default="data/splits")
    parser.add_argument("--output", default="reports/metadata_baseline.json")
    parser.add_argument("--n-splits", type=int, default=DEFAULT_N_SPLITS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Translate CLI arguments into one baseline evaluation call."""
    args = build_argument_parser().parse_args(argv)
    summary = run_baseline(
        args.raw_dir,
        args.splits_dir,
        args.output,
        n_splits=args.n_splits,
        seed=args.seed,
    )

    print("Metadata-only baseline (subject-level ROC-AUC)")
    print(f"Features: {', '.join(FEATURES)}\n")
    for drawing_type, result in summary["results"].items():
        folds = ", ".join(f"{score:.3f}" for score in result["fold_auc"])
        print(
            f"  {drawing_type:<8}: {result['mean_auc']:.3f} "
            f"+/- {result['std_auc']:.3f}   (folds: {folds})"
        )
    print(f"\nAny model must clearly exceed {summary['highest_mean_auc']:.3f}.")
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
