import logging
import os
import sys
from datetime import datetime
from logging import FileHandler
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from backend.config.settings import (LOG_BACKUP_COUNT, LOG_CONSOLE_LEVEL, LOG_DIR, LOG_LEVEL, LOG_ROTATION_INTERVAL, LOG_ROTATION_WHEN, TIMING_ENABLED, TIMING_RUN_LOGS_KEEP)

def _build_rotating_handler(log_path: Path, level: int, formatter: logging.Formatter) -> TimedRotatingFileHandler:
    handler = TimedRotatingFileHandler(log_path, when=LOG_ROTATION_WHEN, interval=LOG_ROTATION_INTERVAL, backupCount=LOG_BACKUP_COUNT, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler

def _prune_old_timing_logs(timing_log_dir: Path) -> None:
    if TIMING_RUN_LOGS_KEEP <= 0:
        return

    timing_logs = sorted(timing_log_dir.glob("timing-*.log"), key=lambda path: path.stat().st_mtime, reverse=True)
    for old_log in timing_logs[TIMING_RUN_LOGS_KEEP:]:
        try:
            old_log.unlink()
        except OSError:
            logging.getLogger(__name__).warning("Unable to remove old timing log '%s'", old_log)

def _setup_timing_logger(timing_log_dir: Path) -> None:
    timing_logger = logging.getLogger("backend.timing")
    timing_logger.setLevel(logging.INFO)
    timing_logger.propagate = False

    if timing_logger.hasHandlers():
        timing_logger.handlers.clear()

    if not TIMING_ENABLED:
        return

    timing_formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    run_id = f"{datetime.now():%Y%m%d-%H%M%S-%f}-pid{os.getpid()}"
    timing_path = timing_log_dir / f"timing-{run_id}.log"
    timing_handler: FileHandler = FileHandler(timing_path, encoding="utf-8")
    timing_handler.setLevel(logging.INFO)
    timing_handler.setFormatter(timing_formatter)
    timing_logger.addHandler(timing_handler)
    timing_logger.info("run_started | run_id=%s | pid=%s", run_id, os.getpid())
    _prune_old_timing_logs(timing_log_dir)

def setup_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))

    line_formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    console_formatter = logging.Formatter("%(levelname)-8s: %(message)s")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_CONSOLE_LEVEL, logging.INFO))
    console_handler.setFormatter(console_formatter)

    log_root = Path(LOG_DIR)
    error_log_dir = log_root / "errors"
    timing_log_dir = log_root / "timing"
    error_log_dir.mkdir(parents=True, exist_ok=True)
    timing_log_dir.mkdir(parents=True, exist_ok=True)

    error_file_handler = _build_rotating_handler(error_log_dir / "errors.log", logging.ERROR, line_formatter)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(console_handler)
    logger.addHandler(error_file_handler)
    _setup_timing_logger(timing_log_dir)
