"""Example: Using VoiceForge Local from another AI project."""

from voiceforge_client import VoiceForge

vf = VoiceForge()

result = vf.speak(
    voice="my_voice",
    text="Namaste. System ready.",
    language="hi"
)

result.save("hello.wav")
print("Saved hello.wav")