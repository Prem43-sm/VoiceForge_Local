"""Audio analysis utilities for quality assessment."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf


@dataclass
class AudioQualityReport:
    """Audio quality assessment results."""

    file_path: str
    duration: float
    sample_rate: int
    channels: int
    rms_loudness: float
    peak_level: float
    clipping: bool
    silence_ratio: float
    speech_ratio: float
    snr_estimate: float | None = None
    dc_offset: float = 0.0
    quality_score: int = 0
    quality_label: str = "Unknown"
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "rms_loudness": self.rms_loudness,
            "peak_level": self.peak_level,
            "clipping": self.clipping,
            "silence_ratio": self.silence_ratio,
            "speech_ratio": self.speech_ratio,
            "snr_estimate": self.snr_estimate,
            "dc_offset": self.dc_offset,
            "quality_score": self.quality_score,
            "quality_label": self.quality_label,
            "issues": self.issues,
        }


class AudioAnalyzer:
    """Analyzes audio files and produces quality reports."""

    def analyze(self, file_path: Path | str) -> AudioQualityReport:
        """Analyze an audio file and return a quality report."""
        file_path = Path(file_path)
        issues: list[str] = []

        data, sample_rate = sf.read(str(file_path), always_2d=True)
        duration = len(data) / sample_rate
        channels = data.shape[1] if data.ndim > 1 else 1

        # Convert to mono for analysis
        mono = np.mean(data, axis=1) if data.ndim > 1 else data.flatten()

        # RMS loudness
        rms = float(np.sqrt(np.mean(mono**2)))

        # Peak level
        peak = float(np.max(np.abs(mono)))

        # Clipping detection (samples at or near ±1.0)
        clipping = bool(np.any(np.abs(mono) >= 0.99))
        if clipping:
            issues.append("Audio may be clipping")

        # Silence ratio
        silence_threshold = 0.01
        silence_samples = int(np.sum(np.abs(mono) < silence_threshold))
        silence_ratio = float(silence_samples / len(mono))
        if silence_ratio > 0.5:
            issues.append("High silence ratio")

        # Speech ratio (inverse of silence roughly)
        speech_ratio = 1.0 - silence_ratio

        # DC offset
        dc_offset = float(np.mean(mono))
        if abs(dc_offset) > 0.05:
            issues.append("Significant DC offset")

        # SNR estimate (rough)
        snr_estimate: float | None = None
        if rms > 0:
            snr_estimate = 20.0 * np.log10(peak / rms) if peak > 0 else None

        # Quality score 0-100
        quality_score = 100
        if clipping:
            quality_score -= 20
        if silence_ratio > 0.5:
            quality_score -= 15
        if abs(dc_offset) > 0.05:
            quality_score -= 10
        if peak < 0.1:
            quality_score -= 15
            issues.append("Very low volume")
        if peak > 0.9:
            quality_score -= 10
            issues.append("Volume near maximum")
        if duration < 1.0:
            quality_score -= 20
            issues.append("Audio is very short")
        quality_score = max(0, min(100, quality_score))

        if quality_score >= 90:
            quality_label = "Excellent"
        elif quality_score >= 75:
            quality_label = "Very Good"
        elif quality_score >= 60:
            quality_label = "Good"
        elif quality_score >= 40:
            quality_label = "Fair"
        else:
            quality_label = "Poor"

        return AudioQualityReport(
            file_path=str(file_path),
            duration=duration,
            sample_rate=sample_rate,
            channels=channels,
            rms_loudness=rms,
            peak_level=peak,
            clipping=clipping,
            silence_ratio=silence_ratio,
            speech_ratio=speech_ratio,
            snr_estimate=snr_estimate,
            dc_offset=dc_offset,
            quality_score=quality_score,
            quality_label=quality_label,
            issues=issues,
        )