"""
Logging configuration for the payments service.

TODO(TEAM-PLATFORM): Migrate to structured logging library (structlog).
"""

import logging
import sys
from typing import Any


def configure_logging() -> None:
    """Configure the root logger."""
    # TODO(TEAM-PLATFORM): Replace with JSON logging format
    legacy_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
    
    logging.basicConfig(
        level=logging.INFO,
        format=legacy_format,
        stream=sys.stdout,
    )
    
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with structured logging support.
    
    This is the preferred way to get a logger in the application.
    """
    return logging.getLogger(name)


class LegacyLogger:
    """
    Legacy logger for backward compatibility.
    
    TODO(TEAM-PLATFORM): Remove after all services migrated.
    """
    
    def __init__(self, name: str):
        self._logger = logging.getLogger(name)
    
    def info(self, message: str, *args: Any) -> None:
        logging.info(message % args if args else message)
    
    def warning(self, message: str, *args: Any) -> None:
        logging.warning(message % args if args else message)
    
    def error(self, message: str, *args: Any) -> None:
        logging.error(message % args if args else message)


def get_legacy_logger(name: str) -> LegacyLogger:
    """
    Get a legacy logger instance.
    
    TODO(TEAM-PLATFORM): Remove after migration.
    """
    return LegacyLogger(name)
