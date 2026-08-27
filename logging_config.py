import json
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.jsonl")

os.makedirs(LOG_DIR, exist_ok=True)


class JsonFormatter(logging.Formatter):
    """Formats log records as one JSON object per line."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "level": record.levelname,
            "module": record.name,
            "event": record.getMessage()
        }

        # Add optional structured fields
        if hasattr(record, "details"):
            log_data["details"] = record.details

        return json.dumps(log_data)


def get_logger(name: str) -> logging.Logger:
    """Returns a centrally configured application logger."""

    logger = logging.getLogger(name)

    # Prevent duplicate handlers if the function is called multiple times.
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    # ---------------- CONSOLE HANDLER ----------------
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler.setFormatter(console_formatter)

    # ---------------- JSON FILE HANDLER ----------------
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(JsonFormatter())

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger