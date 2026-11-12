# VoiceForge Local

Offline Voice Clone & Reusable Voice Pack Studio for Windows.

A complete, production-minded, FREE, LOCAL Windows PC application that lets a user
provide one or more authorized voice recordings, process them, create a reusable
voice profile/voice pack, and then use that voice pack from other AI projects to
synthesize speech locally.

## Features

- **Voice Pack Creation**: Create reusable voice profiles from authorized recordings
- **Local TTS**: Synthesize speech locally without cloud APIs
- **REST API**: Local HTTP API on `http://127.0.0.1:8765` for integration with other AI projects
- **Python SDK**: Tiny client package for other projects
- **CLI**: Command-line interface for automation
- **Voice Pack Portability**: Export/import `.voicepack` ZIP files
- **Audio Analysis**: Quality scoring, silence detection, clipping detection
- **Preprocessing**: Non-destructive audio cleaning pipeline
- **Hardware Detection**: Auto-detects CPU/GPU/CUDA/VRAM
- **Hindi + English**: Multilingual TTS support (engine dependent)
- **Privacy First**: No telemetry, no cloud upload, all processing local

## Architecture

```
Desktop UI (PySide6)
    ↓
Project Manager
    ↓
Audio Ingestion → Preprocessing → Voice Cloning Engine → TTS Synthesis
    ↓
Voice Pack Manager → Local Storage (.voicepack ZIP)
    ↓
Local REST API (127.0.0.1:8765) → Python SDK / CLI
```

## Installation

### Quick Setup (Windows)

```powershell
# Clone or extract this repository
cd VoiceForge-Local

# Run the setup script
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\setup_windows.ps1

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run diagnostics
voiceforge doctor

# Start the local API server
voiceforge server
```

### Manual Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements/core.txt
pip install -r requirements/gpu.txt  # Optional: for GPU support
```

## Usage

### Create a Voice Pack (GUI)

1. Launch: `python app/main.py`
2. Click **[Create Voice Pack]**
3. Check the authorization checkbox (required)
4. Drop your authorized MP3/WAV files
5. Analyze and preprocess the audio
6. Select reference clips
7. Choose engine and create the voice pack
8. Test with sample text
9. Save the voice pack

### CLI Usage

```powershell
# List voice packs
voiceforge list-voices

# Analyze an audio file
voiceforge analyze-audio recording.mp3

# Test a voice pack
voiceforge test --voice vf_abc123 --text "Hello, system ready." --output output.wav

# Start the API server
voiceforge server

# Run diagnostics
voiceforge doctor
```

### Python SDK

```python
from voiceforge_client import VoiceForge

vf = VoiceForge("http://127.0.0.1:8765")
audio = vf.speak(
    voice="my-voice",
    text="Namaste. Main aapki madad ke liye taiyar hoon.",
    language="hi"
)
audio.save("output.wav")
```

### REST API

```bash
curl -X POST http://127.0.0.1:8765/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"voice_id": "my-voice", "text": "Hello, system ready.", "language": "en", "output_format": "wav"}' \
  --output output.wav
```

## Voice Pack Format

A voice pack is a directory (or `.voicepack` ZIP) containing:

```
voice_packs/
└── vf_abc123/
    ├── voicepack.json          # Metadata schema
    ├── speaker_embedding.bin   # Speaker representation
    ├── reference_audio/        # Authorized reference recordings
    ├── preview/                # Preview audio
    ├── metadata/               # Source info, preprocessing config
    └── engine/                 # Engine-specific config
```

## Legal / Responsible Use

- Only clone voices you have authorization to use
- Do not use for impersonation, fraud, or deception
- Authorization confirmation is stored in voice pack metadata
- See `docs/RESPONSIBLE_USE.md` for details

## Model Licenses

See `docs/MODEL_LICENSES.md` for information about bundled/downloadable models.

## Limitations

- Voice cloning quality depends on reference audio quality and model
- Very short audio may produce unstable results
- Background noise can affect cloning
- CPU inference can be slow
- This is an MVP - not all advanced features are implemented

## Project Structure

```
voiceforge-local/
├── app/                    # Application source code
├── config/                 # Configuration files
├── data/                   # Runtime data (models, voice packs, outputs, logs)
├── docs/                   # Documentation
├── examples/               # Example projects
├── requirements/           # Python dependency files
├── scripts/                # Setup and utility scripts
├── tests/                  # Unit and integration tests
├── pyproject.toml
├── setup_windows.ps1
├── README.md
└── LICENSE
```

## License

MIT License