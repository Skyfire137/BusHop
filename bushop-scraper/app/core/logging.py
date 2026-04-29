# app/core/logging.py
import json
import logging
from datetime import UTC, datetime

_EXTRA_FIELDS = ("job_id", "provider", "route_id", "duration_ms", "status", "error")


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        for key in _EXTRA_FIELDS:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with structured JSON formatter.

    Args:
        level: Logging level string (e.g. "INFO", "DEBUG"). Case-insensitive.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger.

    Args:
        name: Logger name, typically ``__name__`` of the calling module.

    Returns:
        Standard :class:`logging.Logger` instance.
    """
    return logging.getLogger(name)
