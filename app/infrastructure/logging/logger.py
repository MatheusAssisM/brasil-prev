from __future__ import annotations

import logging
import sys
from typing import Optional, Dict, Any

from pythonjsonlogger.json import JsonFormatter
from app.core.interfaces import Logger


class CustomJsonFormatter(JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp
        log_record["timestamp"] = self.formatTime(record, self.datefmt)

        # Add level name
        log_record["level"] = record.levelname

        # Add logger name
        log_record["logger"] = record.name

        # Add module and function
        log_record["module"] = record.module
        log_record["function"] = record.funcName

        # Add game context if available
        if hasattr(record, "game_id"):
            log_record["game_id"] = record.game_id
        if hasattr(record, "round_number"):
            log_record["round_number"] = record.round_number


def setup_logging(log_level: str = "INFO") -> None:
    """
    Setup structured JSON logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Get root logger
    root_logger = logging.getLogger()

    # Set level
    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers = []

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create JSON formatter
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(logger)s %(module)s %(function)s %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add handler to root logger
    root_logger.addHandler(console_handler)


class StructuredLogger(Logger):
    """Structured logger implementation using Python's logging module."""

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def debug(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self._logger.debug(msg, extra=extra or {})

    def info(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self._logger.info(msg, extra=extra or {})

    def warning(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self._logger.warning(msg, extra=extra or {})

    def error(
        self, msg: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False
    ) -> None:
        self._logger.error(msg, extra=extra or {}, exc_info=exc_info)
