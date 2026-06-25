import logging
import os
from datetime import datetime

LOG_DIR = "data/logs"

def setup_logger(name: str = "app", level=logging.INFO) -> logging.Logger:
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
    file_path = os.path.join(LOG_DIR, log_filename)

    file_handler = logging.FileHandler(file_path, encoding="utf-8")
    file_handler.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] → %(message)s",
        datefmt="%H:%M:%S"
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # ❌ NO console handler → no terminal spam
    logger.propagate = False  # prevents root logger printing

    return logger