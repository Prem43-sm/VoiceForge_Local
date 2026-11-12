"""Abstract base class for voice engines."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EngineCapability:
    """Describes what a voice engine can do."""

    languages: list[str] = field(default_factory=lambda: ["en"])
    sample_rates: list[int] = field(default_factory=lambda: [24000])
    supports_zero_shot: bool = True
    supports_finetuning: bool = False
    supports_streaming: bool = False
    supports_pitch: bool = False
    supports_speed: bool = True
    min_vram_gb: float = 0.0
    recommended_vram_gb: float = 2.0
    license: str = "unknown"
    offline: bool = True

    def supports_language(self, lang: str) -> bool:
        return lang in self.languages


@dataclass
class SynthesisResult:
    """Result of a TTS synthesis call."""

    audio_path: str
    audio_bytes: bytes | None = None
    sample_rate: int = 24000
    duration_seconds: float = 0.0
    request_id: str = ""
    engine_id: str = ""
    voice_id: str = ""
    text: str = ""
    language: str = "en"
    rtf: float = 0.0


class VoiceEngine:
    """Abstract base interface for all voice cloning/TTS engines."""

    id: str = "base"
    name: str = "Base Engine"
    version: str = "0.1.0"

    def capabilities(self) -> EngineCapability:
        """Return engine capabilities."""
        return EngineCapability()

    def load_model(self) -> None:
        """Load the model into memory/VRAM."""
        raise NotImplementedError

    def unload_model(self) -> None:
        """Unload the model to free resources."""
        raise NotImplementedError

    def is_loaded(self) -> bool:
        """Return True if the model is currently loaded."""
        return False

    def create_voice_profile(
        self, reference_files: list[str], options: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Create a speaker profile/embedding from reference audio files."""
        raise NotImplementedError

    def synthesize(
        self,
        text: str,
        voice_profile: dict[str, Any],
        options: dict[str, Any] | None = None,
    ) -> SynthesisResult:
        """Synthesize text to speech using a voice profile."""
        raise NotImplementedError

    def validate_voice_profile(self, voice_profile: dict[str, Any]) -> bool:
        """Validate that a voice profile is compatible with this engine."""
        return False

    def estimate_resources(self) -> dict[str, Any]:
        """Estimate VRAM/RAM requirements for this engine."""
        return {
            "min_vram_gb": 0.0,
            "recommended_vram_gb": 2.0,
            "supports_cpu": True,
        }