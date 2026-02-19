import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from backend.config.settings import (LOG_BACKUP_COUNT, LOG_CONSOLE_LEVEL, LOG_DIR, LOG_LEVEL, LOG_ROTATION_INTERVAL, LOG_ROTATION_WHEN, TIMING_ENABLED)

class MaxLevelFilter(logging.Filter):
    """Allow records up to (and including) max level."""

    def __init__(self, max_level: int) -> None:
        super().__init__()
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.max_level

def _build_rotating_handler(log_path: Path, level: int, formatter: logging.Formatter) -> TimedRotatingFileHandler:
    handler = TimedRotatingFileHandler(log_path, when=LOG_ROTATION_WHEN, interval=LOG_ROTATION_INTERVAL, backupCount=LOG_BACKUP_COUNT, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler

def _setup_timing_logger(log_dir: Path) -> None:
    timing_logger = logging.getLogger("backend.timing")
    timing_logger.setLevel(logging.INFO)
    timing_logger.propagate = False

    if timing_logger.hasHandlers():
        timing_logger.handlers.clear()

    if not TIMING_ENABLED:
        return

    timing_formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    timing_handler = _build_rotating_handler(log_dir / "timing.log", logging.INFO, timing_formatter)
    timing_logger.addHandler(timing_handler)

def setup_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))

    line_formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_CONSOLE_LEVEL, logging.INFO))
    console_handler.setFormatter(line_formatter)

    log_dir = Path(LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    app_file_handler = _build_rotating_handler(log_dir / "app.log", getattr(logging, LOG_LEVEL, logging.DEBUG), line_formatter)
    app_file_handler.addFilter(MaxLevelFilter(logging.WARNING))

    error_file_handler = _build_rotating_handler(log_dir / "errors.log", logging.ERROR, line_formatter)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(console_handler)
    logger.addHandler(app_file_handler)
    logger.addHandler(error_file_handler)
    _setup_timing_logger(log_dir)
