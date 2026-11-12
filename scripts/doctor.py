"""Doctor utility - standalone diagnostics script."""

from __future__ import annotations

import sys

from app.config.settings import get_settings
from app.core.hardware import detect_hardware, format_hardware_summary
from app.core.logging import setup_logging, get_logger
from app.database.connection import init_db

logger = get_logger("doctor")


def run_doctor() -> int:
    print("VoiceForge Local - Doctor Diagnostics")
    print("=" * 50)

    settings = get_settings()
    print(f"Python: {sys.version.split()[0]}")
    print(f"App version: {settings.app_version}")

    hw = detect_hardware()
    print()
    print(format_hardware_summary(hw))

    print()
    print("Directories:")
    for name, path in [
        ("models", settings.model_dir),
        ("voice_packs", settings.voice_pack_dir),
        ("outputs", settings.output_dir),
        ("cache", settings.cache_dir),
        ("logs", settings.log_dir),
    ]:
        from pathlib import Path
        exists = Path(path).exists()
        status = "OK" if exists else "MISSING"
        print(f"  {name}: {path} ({status})")

    print()
    try:
        init_db(settings.db_path)
        print(f"Database: {settings.db_path} (OK)")
    except Exception as exc:
        print(f"Database: {settings.db_path} (FAIL: {exc})")

    print()
    print("Doctor check complete.")
    return 0


if __name__ == "__main__":
    setup_logging()
    sys.exit(run_doctor())