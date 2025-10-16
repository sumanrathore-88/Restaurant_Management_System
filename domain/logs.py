
import logging
from logging.handlers import RotatingFileHandler
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs.txt')


def setup_logger():
    logger = logging.getLogger('chatora')
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
    fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger
