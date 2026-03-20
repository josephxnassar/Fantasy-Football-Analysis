"""Very simple logging setup for console, errors, and timing."""

import logging
import sys
from pathlib import Path

def setup_logging() -> None:
    """Configure basic console logging plus simple error and timing files."""
    # Root logging captures normal module loggers, so warnings/errors naturally flow here.
    root_logger = _reset_logger(None, logging.INFO)
    
    console_handler = _build_console_handler(logging.INFO)
    root_logger.addHandler(console_handler)

    log_root = Path("backend/logs")
    log_root.mkdir(parents=True, exist_ok=True)

    warning_handler = _build_file_handler(log_root / "warnings.log", logging.WARNING, "%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    warning_handler.addFilter(lambda record: record.levelno == logging.WARNING)
    root_logger.addHandler(warning_handler)

    error_handler = _build_file_handler(log_root / "errors.log", logging.ERROR, "%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    root_logger.addHandler(error_handler)

    # Timing logging stays separate so timing entries only go to timing.log.
    timing_logger = _reset_logger("backend.timing", logging.INFO, propagate=False)

    timing_handler = _build_file_handler(log_root / "timing.log", logging.INFO, "%(asctime)s | %(message)s")
    timing_logger.addHandler(timing_handler)

def _reset_logger(name: str | None, level: int, propagate: bool = True) -> logging.Logger:
    """Get a logger, reset its handlers, and apply basic settings."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    logger.propagate = propagate
    return logger

def _build_console_handler(level: int) -> logging.StreamHandler:
    """Create the basic console handler for app output."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    return handler

def _build_file_handler(path: Path, level: int, message_format: str) -> logging.FileHandler:
    """Create a basic file handler with the shared timestamp format."""
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(message_format, datefmt="%Y-%m-%d %H:%M:%S"))
    return handler
