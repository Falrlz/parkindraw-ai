"""Compatibility wrapper for the training CLI now located in `scripts`."""

from scripts.train import DEFAULT_CHECKPOINT_DIR as DEFAULT_CHECKPOINT_DIR
from scripts.train import DEFAULT_CONFIG as DEFAULT_CONFIG
from scripts.train import build_argument_parser as build_argument_parser
from scripts.train import main as main

from parkindraw.training.config import load_training_config

# Temporary compatibility alias for callers of the original CLI module.
load_config = load_training_config


if __name__ == "__main__":
    raise SystemExit(main())
