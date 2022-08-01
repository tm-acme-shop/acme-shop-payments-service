"""Logging configuration for the payments service."""

import logging
import sys


def configure_logging() -> None:
    """Configure the root logger."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with structured logging support."""
    return logging.getLogger(name)
