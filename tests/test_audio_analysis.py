"""Tests for audio analysis."""

import numpy as np
import soundfile as sf
import tempfile
from pathlib import Path

from app.audio.analysis import AudioAnalyzer


def test_analyze_silent_audio():
    """Test analyzing silent audio."""
    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = Path(tmpdir) / "silent.wav"
        # Create 1 second of silence at 24000 Hz
        data = np.zeros(24000, dtype=np.float32)
        sf.write(str(wav_path), data, 24000)

        analyzer = AudioAnalyzer()
        report = analyzer.analyze(wav_path)

        assert report.duration > 0
        assert report.sample_rate == 24000
        assert report.rms_loudness == 0.0
        assert report.peak_level == 0.0
        assert report.quality_score < 100  # Silent audio should score low