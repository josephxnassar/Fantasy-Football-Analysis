import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from backend.config.settings import (
    ERROR_RUN_LOGS_KEEP,
    LOG_CONSOLE_LEVEL,
    LOG_DIR,
    LOG_LEVEL,
    TIMING_ENABLED,
    TIMING_RUN_LOGS_KEEP,
)


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))

    line_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_CONSOLE_LEVEL, logging.INFO))
    console_handler.setFormatter(console_formatter)

    log_root = Path(LOG_DIR)
    error_log_dir = log_root / "errors"
    timing_log_dir = log_root / "timing"
    error_log_dir.mkdir(parents=True, exist_ok=True)
    timing_log_dir.mkdir(parents=True, exist_ok=True)

    run_id = _build_run_id()

    _reset_logger_handlers(root_logger)

    root_logger.addHandler(console_handler)
    setup_error_logger(root_logger, error_log_dir, run_id, line_formatter)
    setup_timing_logger(timing_log_dir, run_id)

def _build_run_id() -> str:
    return f"{datetime.now():%Y%m%d-%H%M%S-%f}-pid{os.getpid()}"

def _reset_logger_handlers(logger: logging.Logger) -> None:
    if logger.hasHandlers():
        logger.handlers.clear()

def setup_error_logger(root_logger: logging.Logger, error_log_dir: Path, run_id: str, formatter: logging.Formatter) -> None:
    _setup_run_file_logger(
        root_logger,
        log_dir=error_log_dir,
        filename_prefix="errors",
        run_id=run_id,
        level=logging.ERROR,
        formatter=formatter,
        keep_count=ERROR_RUN_LOGS_KEEP,
    )

def setup_timing_logger(timing_log_dir: Path, run_id: str) -> None:
    timing_logger = logging.getLogger("backend.timing")
    timing_logger.setLevel(logging.INFO)
    timing_logger.propagate = False
    _reset_logger_handlers(timing_logger)
    if not TIMING_ENABLED:
        return

    timing_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    _setup_run_file_logger(
        timing_logger,
        log_dir=timing_log_dir,
        filename_prefix="timing",
        run_id=run_id,
        level=logging.INFO,
        formatter=timing_formatter,
        keep_count=TIMING_RUN_LOGS_KEEP,
    )

def _setup_run_file_logger(logger: logging.Logger, log_dir: Path, filename_prefix: str, run_id: str, level: int, formatter: logging.Formatter, keep_count: int) -> None:
    log_path = log_dir / f"{filename_prefix}-{run_id}.log"
    file_handler = _build_file_handler(log_path, level, formatter)
    logger.addHandler(file_handler)
    _prune_old_logs(log_dir, f"{filename_prefix}-*.log", keep_count)

def _build_file_handler(log_path: Path, level: int, formatter: logging.Formatter) -> logging.FileHandler:
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler

def _prune_old_logs(log_dir: Path, pattern: str, keep_count: int) -> None:
    if keep_count <= 0:
        return

    log_files = sorted(log_dir.glob(pattern), key=lambda path: path.stat().st_mtime, reverse=True)
    for old_log in log_files[keep_count:]:
        try:
            old_log.unlink()
        except OSError:
            logging.getLogger(__name__).warning("Unable to remove old log '%s'", old_log)
