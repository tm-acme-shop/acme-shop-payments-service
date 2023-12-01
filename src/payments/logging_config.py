"""
Logging configuration for the payments service.

This module provides both legacy logging (for backward compatibility)
and structured logging (the new standard).

TODO(TEAM-PLATFORM): Migrate all services to structured logging
"""

import logging
import sys
from typing import Any, Optional

from payments.config import get_settings


def configure_logging() -> None:
    """
    Configure the root logger for the application.
    
    TODO(TEAM-PLATFORM): Replace with structured logging library (structlog)
    """
    settings = get_settings()
    
    # Legacy format - TODO(TEAM-PLATFORM): Remove after migration
    legacy_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=legacy_format,
        stream=sys.stdout,
    )
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with structured logging support.
    
    This is the preferred way to get a logger in the application.
    Uses the extra parameter for structured fields.
    
    Usage:
        logger = get_logger(__name__)
        logger.info("Processing payment", extra={"payment_id": "123", "amount": 100})
    """
    return logging.getLogger(name)


class LegacyLogger:
    """
    Legacy logger for backward compatibility.
    
    TODO(TEAM-PLATFORM): Remove this class after all services migrated.
    
    This class mimics the old logging patterns for services that haven't
    migrated to structured logging yet.
    """
    
    def __init__(self, name: str):
        self._logger = logging.getLogger(name)
    
    def info(self, message: str, *args: Any) -> None:
        """Log info message with printf-style formatting."""
        # Legacy pattern: log.Infof("message: %s", value)
        logging.info(message % args if args else message)
    
    def warning(self, message: str, *args: Any) -> None:
        """Log warning message with printf-style formatting."""
        logging.warning(message % args if args else message)
    
    def error(self, message: str, *args: Any) -> None:
        """Log error message with printf-style formatting."""
        logging.error(message % args if args else message)
    
    def debug(self, message: str, *args: Any) -> None:
        """Log debug message with printf-style formatting."""
        logging.debug(message % args if args else message)


def get_legacy_logger(name: str) -> LegacyLogger:
    """
    Get a legacy logger instance.
    
    TODO(TEAM-PLATFORM): Remove this function after migration.
    
    Use get_logger() for new code.
    """
    return LegacyLogger(name)


class StructuredLogAdapter(logging.LoggerAdapter):
    """
    Adapter that adds structured context to all log messages.
    
    Usage:
        logger = StructuredLogAdapter(get_logger(__name__), {"service": "payments"})
        logger.info("message", extra={"key": "value"})
    """
    
    def __init__(
        self,
        logger: logging.Logger,
        extra: Optional[dict[str, Any]] = None,
    ):
        super().__init__(logger, extra or {})
    
    def process(
        self,
        msg: str,
        kwargs: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        """Add default extra fields to kwargs."""
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs


def create_request_logger(
    logger: logging.Logger,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> StructuredLogAdapter:
    """
    Create a logger with request context.
    
    Usage:
        req_logger = create_request_logger(logger, request_id="abc123")
        req_logger.info("Processing request")
    """
    extra: dict[str, Any] = {}
    if request_id:
        extra["request_id"] = request_id
    if user_id:
        extra["user_id"] = user_id
    
    return StructuredLogAdapter(logger, extra)
