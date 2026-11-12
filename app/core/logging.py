"""Structured logging for VoiceForge Local."""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

from app.config.settings import get_settings


def setup_logging(log_dir: Path | str | None = None, level: str | None = None) -> logging.Logger:
    """Configure rotating file logging and console output.

    Never logs API keys, passwords, or full user audio contents.
    """
    settings = get_settings()
    log_dir_path = Path(log_dir) if log_dir else settings.log_dir
    log_dir_path.mkdir(parents=True, exist_ok=True)

    log_level = getattr(logging, (level or settings.log_level).upper(), logging.INFO)

    logger = logging.getLogger("voiceforge")
    logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates on reconfiguration
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # Rotating file handler
    log_file = log_dir_path / "app.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=settings.log_max_file_size_mb * 1024 * 1024,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    logger.info("VoiceForge Local logging initialized")
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a child logger for the given module name."""
    return logging.getLogger(f"voiceforge.{name}")