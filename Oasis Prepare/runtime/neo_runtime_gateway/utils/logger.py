import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "neo_runtime") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        "logs/neo_runtime.log",
        maxBytes=1024 * 1024 * 5,
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger