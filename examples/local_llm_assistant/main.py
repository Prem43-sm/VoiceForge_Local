"""Example: Local LLM assistant integrated with VoiceForge Local."""

from voiceforge_client import VoiceForge

vf = VoiceForge("http://127.0.0.1:8765")

# Simulate an LLM generating text
response_text = "Namaste. Main aapki madad ke liye taiyar hoon."

# Send to VoiceForge for local speech synthesis
audio = vf.speak(
    voice="assistant_voice",
    text=response_text,
    language="hi"
)

audio.save("assistant_response.wav")
print("Assistant response saved.")