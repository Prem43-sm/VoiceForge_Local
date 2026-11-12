"""Tests for configuration module."""

import tempfile
from pathlib import Path

from app.config.settings import Settings, get_settings, reset_settings


def test_settings_defaults():
    """Test that default settings are loaded correctly."""
    reset_settings()
    s = Settings()
    assert s.app_name == "VoiceForge Local"
    assert s.api_port == 8765
    assert s.api_host == "127.0.0.1"
    sample_rate = s.sample_rate
    assert sample_rate == 24000


def test_settings_save_load(tmp_path):
    """Test saving and loading settings."""
    reset_settings()
    config_file = tmp_path / "test_config.toml"
    s = Settings()
    s.api_port = 9999
    s.save(config_file)

    s2 = Settings.load(config_file)
    assert s2.api_port == 9999


def test_get_settings_singleton():
    """Test that get_settings returns a singleton."""
    reset_settings()
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2