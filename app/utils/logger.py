from __future__ import annotations

import logging
import sys
from typing import Optional

from pythonjsonlogger.json import JsonFormatter


class GameContextFilter(logging.Filter):
    """Add game context to log records."""

    def __init__(self):
        super().__init__()
        self.game_id: Optional[str] = None
        self.round_number: Optional[int] = None

    def filter(self, record: logging.LogRecord) -> bool:
        """Add game context fields to the record."""
        if self.game_id:
            record.game_id = self.game_id
        if self.round_number is not None:
            record.round_number = self.round_number
        return True


class CustomJsonFormatter(JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp
        log_record['timestamp'] = self.formatTime(record, self.datefmt)

        # Add level name
        log_record['level'] = record.levelname

        # Add logger name
        log_record['logger'] = record.name

        # Add module and function
        log_record['module'] = record.module
        log_record['function'] = record.funcName

        # Add game context if available
        if hasattr(record, 'game_id'):
            log_record['game_id'] = record.game_id
        if hasattr(record, 'round_number'):
            log_record['round_number'] = record.round_number


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
        '%(timestamp)s %(level)s %(logger)s %(module)s %(function)s %(message)s'
    )
    console_handler.setFormatter(formatter)

    # Add handler to root logger
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Global context filter for game tracing
_game_context_filter = GameContextFilter()


def set_game_context(game_id: Optional[str] = None, round_number: Optional[int] = None) -> None:
    """
    Set game context for logging.

    Args:
        game_id: Unique identifier for the game
        round_number: Current round number
    """
    _game_context_filter.game_id = game_id
    _game_context_filter.round_number = round_number


def clear_game_context() -> None:
    """Clear game context."""
    _game_context_filter.game_id = None
    _game_context_filter.round_number = None


def add_game_context_to_logger(logger: logging.Logger) -> None:
    """
    Add game context filter to a logger.

    Args:
        logger: Logger instance
    """
    logger.addFilter(_game_context_filter)
