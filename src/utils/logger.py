"""
src/utils/logger.py
─────────────────────────────────────────────────────────────────────
Centralised logging: writes to both console and rotating file.
All modules call get_logger(__name__) for consistent formatting.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

_LOG_DIR  = "logs"
_LOG_FILE = os.path.join(_LOG_DIR, "app.log")
_FORMAT   = "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"
_MAX_BYTES   = 5 * 1024 * 1024   # 5 MB per file
_BACKUP_COUNT = 3

# Ensure log directory exists
os.makedirs(_LOG_DIR, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """
    Return a module-level logger.
    Handlers are added only once per logger name (idempotent).
    """
    logger = logging.getLogger(name)

    if logger.handlers:          # Already configured
        return logger

    level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter(_FORMAT, datefmt=_DATE_FMT)

    # ── Console handler ────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ── Rotating file handler ──────────────────────────────────────
    try:
        file_handler = RotatingFileHandler(
            _LOG_FILE,
            maxBytes    = _MAX_BYTES,
            backupCount = _BACKUP_COUNT,
            encoding    = "utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError as exc:
        logger.warning(f"Could not set up file logging: {exc}")

    return logger
