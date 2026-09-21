"""Logging utility for ParkinDraw pipelines and modules."""

import logging
import sys


def get_logger(
    name: str = "parkindraw",
    level: int = logging.INFO,
    ) -> logging.Logger:

    """Get a standardized logger instance with clean formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
