"""Tests for voice pack schema."""

from app.voices.schema import VoicePackSchema, VOICEPACK_VERSION


def test_schema_defaults():
    """Test default schema values."""
    s = VoicePackSchema(name="Test Voice")
    assert s.name == "Test Voice"
    assert s.voicepack_version == VOICEPACK_VERSION
    assert s.id.startswith("vf_")
    assert s.authorization.confirmed is False


def test_schema_validation():
    """Test schema validation."""
    s = VoicePackSchema(name="Test Voice")
    errors = s.validate()
    assert len(errors) > 0  # Missing authorization, engine, references

    s.authorization.confirmed = True
    s.engine.id = "primary"
    s.speaker.reference_files = ["ref1.wav"]
    errors = s.validate()
    assert len(errors) == 0


def test_schema_to_from_dict():
    """Test serialization round-trip."""
    s = VoicePackSchema(
        name="Test Voice",
        display_name="My Test Voice",
        language=["en", "hi"],
    )
    s.authorization.confirmed = True
    s.engine.id = "primary"
    s.speaker.reference_files = ["ref1.wav"]

    d = s.to_dict()
    s2 = VoicePackSchema.from_dict(d)
    assert s2.name == s.name
    assert s2.display_name == s.display_name
    assert s2.language == s.language
    assert s2.id == s.id