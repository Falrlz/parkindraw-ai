"""Command-line entry point for leakage-safe dataset split generation."""

import argparse

from parkindraw.data.splits import (
    DEFAULT_HOLDOUT_SIZE,
    DEFAULT_N_SPLITS,
    DEFAULT_SEED,
    run_split,
)


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the supported split-generation command-line interface."""
    parser = argparse.ArgumentParser(
        prog="parkindraw-create-splits",
        description="Build dataset splits that are safe from subject leakage.",
    )
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--output-dir", default="data/splits")
    parser.add_argument("--holdout-size", type=float, default=DEFAULT_HOLDOUT_SIZE)
    parser.add_argument("--n-splits", type=int, default=DEFAULT_N_SPLITS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Translate CLI arguments into one split-generation call."""
    args = build_argument_parser().parse_args(argv)
    summary = run_split(
        args.raw_dir,
        args.output_dir,
        holdout_size=args.holdout_size,
        n_splits=args.n_splits,
        seed=args.seed,
    )
    print(
        f"Split complete: {summary['total_subjects']} subjects "
        f"({summary['development_subjects']} development, "
        f"{summary['holdout_subjects']} holdout), "
        f"{summary['n_splits']} folds, "
        f"{summary['sessions']} sessions."
    )
    print(f"Duplicate clusters merged: {len(summary['duplicate_clusters'])}")
    print(f"Artifacts: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
