# Troubleshooting

## Common Issues

### FFmpeg not found
Install FFmpeg from https://ffmpeg.org/download.html and add it to your PATH.

### CUDA not available
VoiceForge Local falls back to CPU mode. Synthesis will be slower.

### No model files found
Use the Model Manager to install a TTS model, or run:
```
voiceforge models
```

### Voice pack not found
Make sure the voice pack was created successfully. Use:
```
voiceforge list-voices
```

### API port already in use
Change the port in `config/config.toml` or use a different port.

### Import errors
Make sure you activated the virtual environment and installed dependencies:
```
.venv\Scripts\Activate.ps1
pip install -r requirements/core.txt
```

## Running Doctor

```
voiceforge doctor
```

This checks Python, PyTorch, FFmpeg, CUDA, GPU, VRAM, model files,
permissions, directories, database, and API port.