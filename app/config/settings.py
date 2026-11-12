"""Application configuration loaded from config.toml and environment."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

try:
    import toml
except ImportError:  # pragma: no cover - toml is optional at import time
    toml = None  # type: ignore[assignment]


BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = BASE_DIR / "config" / "config.toml"


@dataclass
class Settings:
    """Application settings."""

    app_name: str = "VoiceForge Local"
    app_version: str = "0.1.0"
    debug: bool = False

    model_dir: Path = field(default_factory=lambda: Path("data/models"))
    voice_pack_dir: Path = field(default_factory=lambda: Path("data/voice_packs"))
    output_dir: Path = field(default_factory=lambda: Path("data/outputs"))
    cache_dir: Path = field(default_factory=lambda: Path("data/cache"))
    log_dir: Path = field(default_factory=lambda: Path("data/logs"))
    db_path: Path = field(default_factory=lambda: Path("data/voiceforge.db"))

    api_host: str = "127.0.0.1"
    api_port: int = 8765
    api_require_token: bool = False
    api_token: str = ""

    prefer_cuda: bool = True
    low_vram_mode: bool = False
    half_precision: bool = False

    default_engine: str = "primary"
    model_id: str = ""
    model_revision: str = ""

    sample_rate: int = 24000
    channels: int = 1
    output_format: str = "wav"

    log_level: str = "INFO"
    log_max_file_size_mb: int = 10
    log_backup_count: int = 5

    @classmethod
    def load(cls, config_file: Path | str | None = None) -> "Settings":
        """Load settings from a TOML config file, falling back to defaults."""
        cfg_path = Path(config_file) if config_file else CONFIG_FILE

        data: dict = {}
        if cfg_path.exists() and toml is not None:
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = toml.load(f)  # type: ignore[arg-type]

        app_cfg = data.get("app", {})
        paths_cfg = data.get("paths", {})
        api_cfg = data.get("api", {})
        gpu_cfg = data.get("gpu", {})
        engine_cfg = data.get("engine", {})
        audio_cfg = data.get("audio", {})
        log_cfg = data.get("logging", {})

        return cls(
            app_name=app_cfg.get("name", "VoiceForge Local"),
            app_version=app_cfg.get("version", "0.1.0"),
            debug=app_cfg.get("debug", False),
            model_dir=Path(paths_cfg.get("model_dir", "data/models")),
            voice_pack_dir=Path(paths_cfg.get("voice_pack_dir", "data/voice_packs")),
            output_dir=Path(paths_cfg.get("output_dir", "data/outputs")),
            cache_dir=Path(paths_cfg.get("cache_dir", "data/cache")),
            log_dir=Path(paths_cfg.get("log_dir", "data/logs")),
            db_path=Path(paths_cfg.get("db_path", "data/voiceforge.db")),
            api_host=api_cfg.get("host", "127.0.0.1"),
            api_port=api_cfg.get("port", 8765),
            api_require_token=api_cfg.get("require_token", False),
            api_token=api_cfg.get("api_token", ""),
            prefer_cuda=gpu_cfg.get("prefer_cuda", True),
            low_vram_mode=gpu_cfg.get("low_vram_mode", False),
            half_precision=gpu_cfg.get("half_precision", False),
            default_engine=engine_cfg.get("default_engine", "primary"),
            model_id=engine_cfg.get("model_id", ""),
            model_revision=engine_cfg.get("model_revision", ""),
            sample_rate=audio_cfg.get("sample_rate", 24000),
            channels=audio_cfg.get("channels", 1),
            output_format=audio_cfg.get("output_format", "wav"),
            log_level=log_cfg.get("level", "INFO"),
            log_max_file_size_mb=log_cfg.get("max_file_size_mb", 10),
            log_backup_count=log_cfg.get("backup_count", 5),
        )

    def save(self, config_file: Path | str | None = None) -> None:
        """Save settings to a TOML config file."""
        if toml is None:
            raise RuntimeError("toml package is required to save config")

        cfg_path = Path(config_file) if config_file else CONFIG_FILE
        cfg_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "app": {
                "name": self.app_name,
                "version": self.app_version,
                "debug": self.debug,
            },
            "paths": {
                "model_dir": str(self.model_dir),
                "voice_pack_dir": str(self.voice_pack_dir),
                "output_dir": str(self.output_dir),
                "cache_dir": str(self.cache_dir),
                "log_dir": str(self.log_dir),
                "db_path": str(self.db_path),
            },
            "api": {
                "host": self.api_host,
                "port": self.api_port,
                "require_token": self.api_require_token,
                "api_token": self.api_token,
            },
            "gpu": {
                "prefer_cuda": self.prefer_cuda,
                "low_vram_mode": self.low_vram_mode,
                "half_precision": self.half_precision,
            },
            "engine": {
                "default_engine": self.default_engine,
                "model_id": self.model_id,
                "model_revision": self.model_revision,
            },
            "audio": {
                "sample_rate": self.sample_rate,
                "channels": self.channels,
                "output_format": self.output_format,
            },
            "logging": {
                "level": self.log_level,
                "max_file_size_mb": self.log_max_file_size_mb,
                "backup_count": self.log_backup_count,
            },
        }

        with open(cfg_path, "w", encoding="utf-8") as f:
            toml.dump(data, f)  # type: ignore[arg-type]


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the singleton settings instance, loading defaults if needed."""
    global _settings
    if _settings is None:
        _settings = Settings.load()
    return _settings


def reset_settings() -> None:
    """Reset the singleton settings (primarily for testing)."""
    global _settings
    _settings = None