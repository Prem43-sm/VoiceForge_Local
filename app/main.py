"""VoiceForge Local - Main application entry point."""

from __future__ import annotations

import sys

from app.config.settings import get_settings
from app.core.hardware import detect_hardware, format_hardware_summary
from app.core.logging import setup_logging, get_logger
from app.database.connection import init_db

logger = get_logger("app")


def main() -> int:
    """Launch VoiceForge Local."""
    setup_logging()
    settings = get_settings()

    logger.info("Starting VoiceForge Local v%s", settings.app_version)

    # Initialize database
    init_db(settings.db_path)

    # Detect hardware
    hw = detect_hardware()
    logger.info("Hardware detected:\n%s", format_hardware_summary(hw))

    logger.info("VoiceForge Local initialized successfully")
    print("VoiceForge Local v0.1.0 - Offline Voice Clone & Reusable Voice Pack Studio")
    print("Run 'voiceforge server' to start the local API, or 'voiceforge doctor' for diagnostics.")
    print("Use the GUI: python -m app.ui.main (when PySide6 is installed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())