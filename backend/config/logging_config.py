import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from backend.config.settings import LOG_LEVEL

def setup_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    file_handler = RotatingFileHandler(log_dir / 'errors.log', maxBytes=1_000_000, backupCount=3)
    file_handler.setLevel(logging.ERROR)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
