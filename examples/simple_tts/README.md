# Simple TTS Example

This example shows how to use VoiceForge Local from another Python project.

```python
from voiceforge_client import VoiceForge

vf = VoiceForge("http://127.0.0.1:8765")

audio = vf.speak(
    voice="my_voice",
    text="Namaste. System ready.",
    language="hi"
)

audio.save("hello.wav")
```

Also supports:
```python
vf.list_voices()
vf.voice_exists("my-voice")
vf.health()
```