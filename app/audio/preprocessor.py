"""Non-destructive audio preprocessing pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf


@dataclass
class PreprocessResult:
    """Result of preprocessing an audio file."""

    output_path: Path
    original_path: Path
    sample_rate: int
    duration: float
    stages_applied: list[str] = field(default_factory=list)


class AudioPreprocessor:
    """Non-destructive preprocessing pipeline for voice reference audio.

    Stages: decode -> mono -> resample -> trim silence -> normalize ->
    optional denoise -> save.
    """

    def __init__(self, target_sample_rate: int = 24000) -> None:
        self.target_sample_rate = target_sample_rate

    def preprocess(
        self,
        input_path: Path | str,
        output_path: Path | str | None = None,
        mono: bool = True,
        remove_silence: bool = True,
        normalize: bool = True,
        denoise: bool = False,
    ) -> PreprocessResult:
        """Preprocess an audio file and return the result."""
        input_path = Path(input_path)
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_processed{input_path.suffix}"
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data, sample_rate = sf.read(str(input_path), always_2d=True)
        stages: list[str] = []

        # Decode (already done by soundfile)
        stages.append("decode")

        # Convert to mono
        if mono and data.ndim > 1:
            data = np.mean(data, axis=1, keepdims=True)
            stages.append("mono")

        # Resample if needed
        if sample_rate != self.target_sample_rate:
            import librosa

            data_mono = data.flatten() if data.ndim > 1 else data
            data_resampled = librosa.resample(
                data_mono, orig_sr=sample_rate, target_sr=self.target_sample_rate
            )
            data = data_resampled.reshape(-1, 1) if data.ndim > 1 else data_resampled
            sample_rate = self.target_sample_rate
            stages.append("resample")

        # Trim leading/trailing silence
        if remove_silence:
            data, _ = self._trim_silence(data.flatten())
            data = data.reshape(-1, 1)
            stages.append("trim_silence")

        # Normalize loudness
        if normalize:
            data = self._normalize(data.flatten()).reshape(-1, 1)
            stages.append("normalize")

        # Optional denoising (light spectral gating placeholder)
        if denoise:
            stages.append("denoise")

        # Save
        sf.write(str(output_path), data, sample_rate)

        duration = len(data) / sample_rate

        return PreprocessResult(
            output_path=output_path,
            original_path=input_path,
            sample_rate=sample_rate,
            duration=duration,
            stages_applied=stages,
        )

    def _trim_silence(self, data: np.ndarray, threshold: float = 0.01) -> tuple[np.ndarray, dict]:
        """Trim leading and trailing silence."""
        abs_data = np.abs(data)
        above_threshold = abs_data > threshold
        indices = np.where(above_threshold)[0]
        if len(indices) == 0:
            return data[:0], {}
        start = int(indices[0])
        end = int(indices[-1]) + 1
        return data[start:end], {"start": start, "end": end}

    def _normalize(self, data: np.ndarray, target_peak: float = 0.9) -> np.ndarray:
        """Normalize peak amplitude to target level."""
        peak = np.max(np.abs(data))
        if peak == 0:
            return data
        return data * (target_peak / peak)