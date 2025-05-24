import logging
import sys

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    file_handler = logging.FileHandler('errors.log')
    file_handler.setLevel(logging.ERROR)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    