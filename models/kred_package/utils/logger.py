"""
utils/logger.py — Centralized logging setup
Provides INFO, ERROR, and DEBUG streams with consistent formatting.
"""

import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Returns a configured logger for the given module name.

    Log level hierarchy:
        DEBUG   → verbose intermediate outputs (pipeline values, parsed JSON)
        INFO    → pipeline flow milestones (engine started, API call made)
        WARNING → non-fatal issues (API fallback triggered)
        ERROR   → API failures, parse failures, missing credentials
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        # Avoid duplicate handlers if module is re-imported
        return logger

    _level = getattr(logging, (level or "INFO").upper(), logging.INFO)
    logger.setLevel(_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(_level)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.propagate = False

    return logger


# Module-level convenience loggers
pipeline_log = get_logger("kred.pipeline")
engine_log    = get_logger("kred.engine")
api_log       = get_logger("kred.api")
