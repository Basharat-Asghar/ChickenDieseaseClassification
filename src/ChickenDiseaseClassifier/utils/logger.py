import logging
import os
from datetime import datetime
from pathlib import Path

LOG_DIR = "logs"

LOG_DIR_PATH = Path(LOG_DIR)
LOG_DIR_PATH.mkdir(exist_ok=True)

LOG_FILE_NAME = f"log_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.log"

LOG_FILE_PATH = LOG_DIR_PATH / LOG_FILE_NAME

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance.
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    return logger