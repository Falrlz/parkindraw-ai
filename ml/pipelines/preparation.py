"""Data preparation pipeline: raw images -> master_manifest.csv."""

import argparse
from pathlib import Path

from src.config.config import (
    DEFAULT_HOLDOUT_SIZE,
    DEFAULT_SEED,
    RAW_DATA_DIR,
    SPLITS_DIR,
)
from src.data.manifest import build_manifest, save_manifest
from src.data.splits import split_holdout, verify_no_leakage
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_preparation_pipeline(
    raw_dir: str | Path = RAW_DATA_DIR,
    output_dir: str | Path = SPLITS_DIR,
    holdout_size: float = DEFAULT_HOLDOUT_SIZE,
    seed: int = DEFAULT_SEED,
    ) -> Path:

    """Execute the data preparation pipeline."""
    logger.info("=== Starting Data Preparation Pipeline ===")

    # Step 1: Scan raw images and resolve anomalies
    logger.info("Step 1: Scanning raw images from '%s'...", raw_dir)
    manifest = build_manifest(raw_dir)

    # Step 2: Lock holdout split on subject clusters
    logger.info("Step 2: Partitioning clinical holdout (%.0f%%, seed=%d)...", holdout_size * 100, seed)
    master_manifest = split_holdout(manifest, holdout_size=holdout_size, seed=seed)

    # Step 3: Verify zero clinical leakage between partitions
    logger.info("Step 3: Verifying zero clinical leakage between partitions...")
    verify_no_leakage(master_manifest)

    # Step 4: Export master manifest artifact
    output_file = Path(output_dir) / "master_manifest.csv"
    logger.info("Step 4: Exporting master manifest to '%s'...", output_file)
    save_manifest(master_manifest, output_file)

    logger.info("=== Data Preparation Completed Successfully ===")
    return output_file


def main(
    argv: list[str] | None = None,
    ) -> int:
    
    """Parse CLI arguments and execute preparation pipeline."""
    parser = argparse.ArgumentParser(description="Prepare dataset and export master_manifest.csv.")
    parser.add_argument("--raw-dir", default=RAW_DATA_DIR, help="Raw dataset directory.")
    parser.add_argument("--output-dir", default=SPLITS_DIR, help="Output splits directory.")
    parser.add_argument("--holdout-size", type=float, default=DEFAULT_HOLDOUT_SIZE, help="Holdout size (0.2).")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed (42).")
    args = parser.parse_args(argv)

    output_file = run_preparation_pipeline(
        raw_dir=args.raw_dir,
        output_dir=args.output_dir,
        holdout_size=args.holdout_size,
        seed=args.seed,
    )
    print(f"Master manifest successfully created: {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
