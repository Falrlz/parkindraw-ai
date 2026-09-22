"""Logging configuration module for ParkinDraw AI Backend Service.

Standardizes logging formats, handlers, and levels across all backend components.
"""

import logging
import sys
from typing import Optional


def setup_logging(level: Optional[str] = "INFO") -> None:
    """Configure system-wide standardized logging format.

    Args:
        level: Log level threshold (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    numeric_level = getattr(logging, (level or "INFO").upper(), logging.INFO)

    log_format = (
        "[%(asctime)s] [%(process)d] [%(levelname)s] "
        "[%(name)s] %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Retrieve a namespaced logger instance.

    Args:
        name: Name of the component requesting the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(f"parkindraw.backend.{name}")
