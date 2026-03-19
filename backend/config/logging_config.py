"""Very simple logging setup for console, errors, and timing."""

import logging
import sys
from pathlib import Path


def setup_logging(level: int = logging.INFO, timing_enabled: bool = True) -> None:
    """Configure basic console logging plus simple error and timing files."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    root_logger.addHandler(console_handler)

    log_root = Path("backend/logs")
    log_root.mkdir(parents=True, exist_ok=True)

    error_handler = logging.FileHandler(log_root / "errors.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root_logger.addHandler(error_handler)

    timing_logger = logging.getLogger("backend.timing")
    timing_logger.setLevel(logging.INFO)
    timing_logger.handlers.clear()
    timing_logger.propagate = False

    if timing_enabled:
        timing_handler = logging.FileHandler(log_root / "timing.log", encoding="utf-8")
        timing_handler.setLevel(logging.INFO)
        timing_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        timing_logger.addHandler(timing_handler)

